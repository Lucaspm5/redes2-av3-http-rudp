import socket
import sys  # Importado caso precise tratar encerramentos limpos
from rudp_common import receber_dados_rudp, enviar_dados_rudp
from http_common import parsear_requisicao, montar_resposta

HOST = '0.0.0.0'
PORT = 5002   # porta dedicada ao HTTP sobre R-UDP

def iniciar():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    print(f"[HTTP-RUDP] Servidor aguardando na porta {PORT}...")
    while True:
        try:
            # Força o socket a resetar o timeout antes de esperar uma nova requisição
            s.settimeout(None) 
            
            dados, addr = receber_dados_rudp(s)
            metodo, caminho = parsear_requisicao(dados)
            resposta = montar_resposta(caminho)
            duracao, retx = enviar_dados_rudp(s, addr, resposta)
            print(f"[HTTP-RUDP] {addr} {metodo} {caminho} -> {len(resposta)} bytes em {duracao:.4f}s ({retx} retransmissoes)")
        except TimeoutError:
            # Se der timeout esperando o próximo cliente, ele apenas ignora e continua rodando
            continue

iniciar()
