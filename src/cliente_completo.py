import sys, time, csv
from dns_client import resolver
import http_client_tcp
import http_client_rudp

def main():
    protocolo = sys.argv[1]
    cenario   = sys.argv[2]
    caminho   = sys.argv[3] if len(sys.argv) > 3 else '/arquivo_1mb.bin'
    execucoes = int(sys.argv[4]) if len(sys.argv) > 4 else 10

    nome_arquivo = caminho.lstrip('/').replace('.', '_')
    csv_total = f'/app/logs/tempototal_{protocolo}_{cenario}_{nome_arquivo}.csv'

    for i in range(1, execucoes + 1):
        ip, t_dns, tentativas = resolver('webserver.local')
        if ip is None:
            print(f"[FLUXO] Exec {i}: DNS falhou apos {tentativas} tentativas, pulando")
            continue
        print(f"[FLUXO] Exec {i}: DNS resolveu webserver.local -> {ip} em {t_dns:.4f}s ({tentativas} tentativas)")

        if protocolo == 'tcp':
            csv_path = f'/app/logs/fluxo_tcp_{cenario}_{nome_arquivo}.csv'
            t_http, thr = http_client_tcp.requisitar(caminho, 'webserver.local', csv_path, i, cenario)
        else:
            csv_path = f'/app/logs/fluxo_rudp_{cenario}_{nome_arquivo}.csv'
            t_http, thr = http_client_rudp.requisitar(caminho, 'webserver.local', csv_path, i, cenario)

        tempo_total = t_dns + t_http
        print(f"[FLUXO] Exec {i}: HTTP={t_http:.4f}s | TOTAL (DNS+HTTP)={tempo_total:.4f}s")

        # Grava tempo total (DNS+HTTP) e taxa de transferencia com DNS incluso
        bytes_aprox = thr * 1_000_000 * t_http / 8  # recupera bytes a partir do throughput HTTP
        throughput_com_dns = (bytes_aprox * 8) / tempo_total / 1_000_000
        with open(csv_total, 'a', newline='') as f:
            csv.writer(f).writerow([i, protocolo.upper(), cenario, t_dns, t_http, tempo_total, throughput_com_dns])

        time.sleep(1)

if __name__ == '__main__':
    main()
