import socket, time, os, csv, sys
from protocolo import montar_pacote, desmontar_pacote, FLAGS_DATA, FLAGS_FIN, HEADER_SIZE

HOST    = '10.0.0.2'
PORT    = 5001
BUFFER  = 4096
TIMEOUT = 2.0
ARQUIVO = '/app/arquivo_teste.bin'

CENARIO = sys.argv[1] if len(sys.argv) > 1 else 'X'
LOG_CSV = f'/app/logs/rudp_cenario_{CENARIO}.csv'

def enviar(execucao):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)

    tamanho = os.path.getsize(ARQUIVO)
    seq     = 0
    inicio  = time.time()

    with open(ARQUIVO, 'rb') as f:
        while True:
            bloco = f.read(BUFFER)
            if not bloco:
                break
            pkt = montar_pacote(seq, 0, FLAGS_DATA, bloco)
            while True:
                s.sendto(pkt, (HOST, PORT))
                try:
                    raw, _ = s.recvfrom(HEADER_SIZE + 10)
                    ack_pkt = desmontar_pacote(raw)
                    if ack_pkt['ack'] == seq:
                        seq += 1
                        break
                except socket.timeout:
                    print(f"[RUDP-{CENARIO}] Timeout seq {seq}, retransmitindo...")

    fin = montar_pacote(seq, 0, FLAGS_FIN)
    while True:
        s.sendto(fin, (HOST, PORT))
        try:
            s.recvfrom(HEADER_SIZE + 10)
            break
        except socket.timeout:
            pass

    s.close()
    fim        = time.time()
    duracao    = fim - inicio
    throughput = (tamanho * 8) / duracao / 1_000_000
    print(f"[RUDP-{CENARIO}] Exec {execucao}: {duracao:.4f}s | {throughput:.4f} Mbps")

    with open(LOG_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([execucao, f'RUDP_{CENARIO}', duracao, throughput])

for i in range(1, 21):
    enviar(i)
    time.sleep(1)
