import socket
from http_common import parsear_requisicao, montar_resposta

HOST = '0.0.0.0'
PORT = 8080

def iniciar():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"[HTTP-TCP] Servidor aguardando na porta {PORT}...")
    while True:
        conn, addr = s.accept()
        dados = conn.recv(8192)
        if dados:
            metodo, caminho = parsear_requisicao(dados)
            resposta = montar_resposta(caminho)
            conn.sendall(resposta)
            print(f"[HTTP-TCP] {addr} {metodo} {caminho} -> {len(resposta)} bytes")
        conn.close()

iniciar()
