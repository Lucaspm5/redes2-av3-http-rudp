import socket, time
from protocolo import (
    montar_pacote, desmontar_pacote, verificar_checksum,
    FLAGS_DATA, FLAGS_ACK, FLAGS_FIN, HEADER_SIZE
)

BUFFER = 4096
TIMEOUT_PADRAO = 0.3

def enviar_dados_rudp(sock, destino, dados: bytes, timeout=TIMEOUT_PADRAO):

    timeout_anterior = sock.gettimeout()
    sock.settimeout(timeout)

    try:
        seq = 0
        retransmissoes = 0
        inicio = time.time()
        offset = 0
        total = len(dados)

        while offset < total:
            bloco = dados[offset:offset + BUFFER]
            pkt = montar_pacote(seq, 0, FLAGS_DATA, bloco)

            while True:
                sock.sendto(pkt, destino)

                try:
                    raw, _ = sock.recvfrom(HEADER_SIZE + 10)
                    ack = desmontar_pacote(raw)

                    if ack['ack'] == seq:
                        seq += 1
                        break

                except socket.timeout:
                    retransmissoes += 1

            offset += len(bloco)

        fin = montar_pacote(seq, 0, FLAGS_FIN)

        while True:
            sock.sendto(fin, destino)

            try:
                sock.recvfrom(HEADER_SIZE + 10)
                break

            except socket.timeout:
                retransmissoes += 1

        duracao = time.time() - inicio
        return duracao, retransmissoes

    finally:
        sock.settimeout(timeout_anterior)


def receber_dados_rudp(sock, buffer_size=BUFFER + HEADER_SIZE):
    """Recebe um fluxo completo via Stop-and-Wait (bloqueante).
    Retorna (dados_recebidos: bytes, endereco_remoto)."""
    esperado = 0
    dados = b''
    origem = None

    while True:
        raw, addr = sock.recvfrom(buffer_size)
        origem = addr
        pkt = desmontar_pacote(raw)

        if pkt['flags'] == FLAGS_FIN:
            ack = montar_pacote(0, pkt['seq'], FLAGS_ACK)
            sock.sendto(ack, addr)
            break

        if not verificar_checksum(pkt):
            continue  # descarta corrompido; forca retransmissao por timeout

        if pkt['seq'] == esperado:
            dados += pkt['dados']
            ack = montar_pacote(0, esperado, FLAGS_ACK)
            sock.sendto(ack, addr)
            esperado += 1
        else:
            if esperado > 0:
                ack = montar_pacote(0, esperado - 1, FLAGS_ACK)
                sock.sendto(ack, addr)

    return dados, origem
