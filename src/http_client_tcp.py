import socket, time, sys, csv
from http_common import montar_requisicao

HOST = '10.0.0.2'
PORT = 8080

def requisitar(caminho, host_logico, csv_path, execucao, cenario):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inicio = time.time()
    s.connect((HOST, PORT))
    req = montar_requisicao(caminho, host_logico)
    s.sendall(req)
    resposta = b''
    while True:
        bloco = s.recv(8192)
        if not bloco:
            break
        resposta += bloco
    s.close()
    duracao = time.time() - inicio
    bytes_totais = len(resposta)
    throughput = (bytes_totais * 8) / duracao / 1_000_000
    print(f"[HTTP-TCP-{cenario}] Exec {execucao} {caminho}: {duracao:.4f}s | {throughput:.4f} Mbps | {bytes_totais}B")
    with open(csv_path, 'a', newline='') as f:
        csv.writer(f).writerow([execucao, f'HTTP_TCP_{cenario}', caminho, duracao, throughput, bytes_totais])
    return duracao, throughput

if __name__ == '__main__':
    cenario = sys.argv[1] if len(sys.argv) > 1 else 'X'
    caminho = sys.argv[2] if len(sys.argv) > 2 else '/arquivo_1mb.bin'
    qtd     = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    nome_arquivo = caminho.lstrip('/').replace('.', '_')
    csv_path = f'/app/logs/http_tcp_{cenario}_{nome_arquivo}.csv'
    for i in range(1, qtd + 1):
        requisitar(caminho, 'webserver.local', csv_path, i, cenario)
        time.sleep(1)
