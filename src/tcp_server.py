import socket, time, os

HOST = '0.0.0.0'
PORT = 5000
BUFFER = 4096

def iniciar():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"[TCP] Servidor aguardando na porta {PORT}...")

    while True:
        conn, addr = s.accept()
        print(f"[TCP] Conectado: {addr}")
        with open("recebido_tcp.bin", "wb") as f:
            inicio = time.time()
            total  = 0
            while True:
                dados = conn.recv(BUFFER)
                if not dados:
                    break
                f.write(dados)
                total += len(dados)
        fim = time.time()
        duracao   = fim - inicio
        throughput = (total * 8) / duracao / 1_000_000  # Mbps
        print(f"[TCP] Recebido: {total} bytes | Tempo: {duracao:.4f}s | Throughput: {throughput:.4f} Mbps")
        conn.close()

iniciar()
