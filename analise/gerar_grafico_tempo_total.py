import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob, os, re

LOG_DIR = '/home/lucas/Redes_2_FINAL/logs'
OUT_DIR = '/home/lucas/Redes_2_FINAL/analise/graficos'
os.makedirs(OUT_DIR, exist_ok=True)

padrao = re.compile(r'tempototal_(tcp|rudp)_([ABCabc])_(.+)\.csv')
linhas = []

for caminho in sorted(glob.glob(f'{LOG_DIR}/tempototal_*.csv')):
    nome = os.path.basename(caminho)
    m = padrao.match(nome)
    if not m:
        continue
    protocolo, cenario, arquivo = m.groups()
    cenario = cenario.upper()
    df = pd.read_csv(caminho, names=['exec','proto','cen','t_dns','t_http','t_total','thr_com_dns'])
    linhas.append({
        'protocolo': protocolo.upper(), 'cenario': cenario, 'arquivo': arquivo,
        'tempo_total_medio': df['t_total'].mean(),
        'tempo_total_desvio': df['t_total'].std(),
        'tempo_dns_medio': df['t_dns'].mean(),
    })

resumo = pd.DataFrame(linhas)
print(resumo.to_string(index=False))
resumo.to_csv(f'{LOG_DIR}/resumo_tempo_total.csv', index=False)

cenarios = ['A', 'B', 'C']
for arquivo in resumo['arquivo'].unique():
    sub = resumo[resumo['arquivo'] == arquivo]
    tcp_vals   = [sub[(sub.cenario==c)&(sub.protocolo=='TCP')]['tempo_total_medio'].values[0]
                  if len(sub[(sub.cenario==c)&(sub.protocolo=='TCP')]) else 0 for c in cenarios]
    rudp_vals  = [sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]['tempo_total_medio'].values[0]
                  if len(sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]) else 0 for c in cenarios]
    tcp_desv   = [sub[(sub.cenario==c)&(sub.protocolo=='TCP')]['tempo_total_desvio'].values[0]
                  if len(sub[(sub.cenario==c)&(sub.protocolo=='TCP')]) else 0 for c in cenarios]
    rudp_desv  = [sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]['tempo_total_desvio'].values[0]
                  if len(sub[(sub.cenario==c)&(sub.protocolo=='RUDP')]) else 0 for c in cenarios]

    x, largura = np.arange(len(cenarios)), 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - largura/2, tcp_vals,  largura, yerr=tcp_desv,  label='TCP (DNS+HTTP)',   color='steelblue', capsize=4)
    ax.bar(x + largura/2, rudp_vals, largura, yerr=rudp_desv, label='R-UDP (DNS+HTTP)', color='coral', capsize=4)
    ax.set_xticks(x); ax.set_xticklabels(cenarios)
    ax.set_ylabel('Tempo total de carregamento (s)')
    ax.set_xlabel('Cenario de rede')
    ax.set_title(f'Tempo Total de Carregamento (DNS+HTTP) — {arquivo}')
    ax.legend(); ax.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(f'{OUT_DIR}/tempototal_{arquivo}.png', dpi=150)
    plt.close()
    print(f"Grafico salvo: tempototal_{arquivo}.png")

print(f"\nGraficos em: {OUT_DIR}")
