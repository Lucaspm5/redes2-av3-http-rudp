import socket
from dns_protocolo import montar_resposta, desmontar, DNS_SIZE

HOST = '0.0.0.0'
PORT = 5300
ZONA = '/app/hosts.txt'

def carregar_zona():
    zona = {}
    with open(ZONA) as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
            nome, ip = linha.split()
            zona[nome] = ip
    return zona

def iniciar():
    zona = carregar_zona()
    print(f"[DNS] Zona carregada: {zona}")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    print(f"[DNS] Servidor aguardando na porta {PORT}...")

    while True:
        raw, addr = s.recvfrom(DNS_SIZE)
        consulta = desmontar(raw)
        nome = consulta['nome']
        ip = zona.get(nome)
        resposta = montar_resposta(consulta['id'], nome, ip)
        s.sendto(resposta, addr)
        status = ip if ip else "NXDOMAIN"
        print(f"[DNS] id={consulta['id']} nome={nome} -> {status}")

iniciar()
