import socket, time, csv
from protocolo import desmontar_pacote, montar_pacote, verificar_checksum, FLAGS_ACK, FLAGS_FIN, HEADER_SIZE

HOST    = '0.0.0.0'
PORT    = 5001
BUFFER  = 4096 + HEADER_SIZE
LOG_CSV = '/app/logs/rudp_resultados.csv'

def iniciar():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    print("[R-UDP] Servidor aguardando...")

    execucao = 0
    while True:
        esperado = 0
        inicio   = None
        total    = 0
        arquivo  = open("recebido_rudp.bin", "wb")

        while True:
            raw, addr = s.recvfrom(BUFFER)
            pkt = desmontar_pacote(raw)

            if inicio is None:
                inicio = time.time()

            if pkt['flags'] == FLAGS_FIN:
                fim        = time.time()
                duracao    = fim - inicio
                throughput = (total * 8) / duracao / 1_000_000
                execucao  += 1
                print(f"[R-UDP] Exec {execucao}: {total}B | {duracao:.4f}s | {throughput:.4f} Mbps")
                ack = montar_pacote(0, pkt['seq'], FLAGS_ACK)
                s.sendto(ack, addr)
                arquivo.close()
                with open(LOG_CSV, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([execucao, 'R-UDP', duracao, throughput])
                break

            if not verificar_checksum(pkt):
                print(f"[R-UDP] Checksum inválido seq {pkt['seq']}")
                continue

            if pkt['seq'] == esperado:
                arquivo.write(pkt['dados'])
                total += len(pkt['dados'])
                ack = montar_pacote(0, esperado, FLAGS_ACK)
                s.sendto(ack, addr)
                esperado += 1
            else:
                if esperado > 0:
                    ack = montar_pacote(0, esperado - 1, FLAGS_ACK)
                    s.sendto(ack, addr)

iniciar()
