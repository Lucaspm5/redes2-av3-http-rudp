import socket, time, csv, os, sys

HOST    = '10.0.0.2'
PORT    = 5000
BUFFER  = 4096
ARQUIVO = '/app/arquivo_teste.bin'

CENARIO = sys.argv[1] if len(sys.argv) > 1 else 'X'
LOG_CSV = f'/app/logs/tcp_cenario_{CENARIO}.csv'

def enviar(execucao):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    tamanho = os.path.getsize(ARQUIVO)
    inicio  = time.time()
    with open(ARQUIVO, 'rb') as f:
        while True:
            bloco = f.read(BUFFER)
            if not bloco:
                break
            s.sendall(bloco)
    s.close()
    fim        = time.time()
    duracao    = fim - inicio
    throughput = (tamanho * 8) / duracao / 1_000_000
    print(f"[TCP-{CENARIO}] Exec {execucao}: {duracao:.4f}s | {throughput:.4f} Mbps")
    with open(LOG_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([execucao, f'TCP_{CENARIO}', duracao, throughput])

for i in range(1, 21):
    enviar(i)
    time.sleep(1)
