import socket, time, sys, csv
from rudp_common import enviar_dados_rudp, receber_dados_rudp
from http_common import montar_requisicao

HOST = '10.0.0.2'
PORT = 5002

def requisitar(caminho, host_logico, csv_path, execucao, cenario):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    req = montar_requisicao(caminho, host_logico)
    inicio = time.time()
    _, retx_envio = enviar_dados_rudp(s, (HOST, PORT), req)
    resposta, _ = receber_dados_rudp(s)
    duracao = time.time() - inicio
    s.close()
    bytes_totais = len(resposta)
    throughput = (bytes_totais * 8) / duracao / 1_000_000
    print(f"[HTTP-RUDP-{cenario}] Exec {execucao} {caminho}: {duracao:.4f}s | {throughput:.4f} Mbps | {bytes_totais}B | retx={retx_envio}")
    with open(csv_path, 'a', newline='') as f:
        csv.writer(f).writerow([execucao, f'HTTP_RUDP_{cenario}', caminho, duracao, throughput, bytes_totais, retx_envio])
    return duracao, throughput

if __name__ == '__main__':
    cenario = sys.argv[1] if len(sys.argv) > 1 else 'X'
    caminho = sys.argv[2] if len(sys.argv) > 2 else '/arquivo_1mb.bin'
    qtd     = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    nome_arquivo = caminho.lstrip('/').replace('.', '_')
    csv_path = f'/app/logs/http_rudp_{cenario}_{nome_arquivo}.csv'
    for i in range(1, qtd + 1):
        requisitar(caminho, 'webserver.local', csv_path, i, cenario)
        time.sleep(1)
