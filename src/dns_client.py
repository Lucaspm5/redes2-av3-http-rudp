import socket, time, random
from dns_protocolo import montar_query, desmontar, DNS_SIZE

DNS_HOST = '10.0.0.4'
DNS_PORT = 5300
TIMEOUT = 2.0
MAX_TENTATIVAS = 3

def resolver(nome):
    """Resolve 'nome' via DNS sobre UDP puro (sem confiabilidade R-UDP).
    Implementa timeout + tentativas limitadas NA APLICACAO, pois o
    UDP nativo nao garante entrega nem detecta perda por si so."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)
    id_consulta = random.randint(0, 65535)
    pkt = montar_query(id_consulta, nome)

    inicio = time.time()
    tentativas = 0
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        tentativas = tentativa
        s.sendto(pkt, (DNS_HOST, DNS_PORT))
        try:
            raw, _ = s.recvfrom(DNS_SIZE)
            resposta = desmontar(raw)
            duracao = time.time() - inicio
            s.close()
            return resposta['ip'], duracao, tentativas
        except socket.timeout:
            print(f"[DNS-Cliente] Timeout na tentativa {tentativa} para '{nome}'")
            continue

    s.close()
    duracao = time.time() - inicio
    return None, duracao, tentativas
