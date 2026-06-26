import re, csv, os

LOG_PATH = '/home/lucas/Redes_2_FINAL/resultado_geral.log'
OUT_DIR  = '/home/lucas/Redes_2_FINAL/logs'

# Captura linhas como:
# === CENARIO A ===
# ---- Protocolo: tcp ----
#   >> Arquivo: arquivo_100kb.bin
# [FLUXO] Exec 1: HTTP=0.0123s | TOTAL (DNS+HTTP)=0.0135s
# (a linha de DNS vem antes, com o tempo de DNS)

cenario_atual = None
protocolo_atual = None
arquivo_atual = None
dns_atual = None

padrao_cenario   = re.compile(r'CENARIO (\w)')
padrao_protocolo = re.compile(r'Protocolo: (\w+)')
padrao_arquivo    = re.compile(r'>> Arquivo: (\S+)')
padrao_dns        = re.compile(r'\[FLUXO\] Exec (\d+): DNS resolveu .* em ([\d.]+)s')
padrao_total      = re.compile(r'\[FLUXO\] Exec (\d+): HTTP=([\d.]+)s \| TOTAL \(DNS\+HTTP\)=([\d.]+)s')

arquivos_csv = {}

with open(LOG_PATH) as f:
    for linha in f:
        m = padrao_cenario.search(linha)
        if m:
            cenario_atual = m.group(1)
            continue
        m = padrao_protocolo.search(linha)
        if m:
            protocolo_atual = m.group(1)
            continue
        m = padrao_arquivo.search(linha)
        if m:
            arquivo_atual = m.group(1).replace('.', '_')
            continue
        m = padrao_dns.search(linha)
        if m:
            dns_atual = float(m.group(2))
            continue
        m = padrao_total.search(linha)
        if m and cenario_atual and protocolo_atual and arquivo_atual and dns_atual is not None:
            exec_num, t_http, t_total = m.group(1), float(m.group(2)), float(m.group(3))
            chave = f'tempototal_{protocolo_atual}_{cenario_atual}_{arquivo_atual}'
            if chave not in arquivos_csv:
                caminho = os.path.join(OUT_DIR, chave + '.csv')
                arquivos_csv[chave] = open(caminho, 'w', newline='')
            writer = csv.writer(arquivos_csv[chave])
            writer.writerow([exec_num, protocolo_atual.upper(), cenario_atual, dns_atual, t_http, t_total, 0])
            dns_atual = None

for f in arquivos_csv.values():
    f.close()

print(f"{len(arquivos_csv)} arquivos CSV gerados em {OUT_DIR}")
for chave in arquivos_csv:
    print(f"  - {chave}.csv")
