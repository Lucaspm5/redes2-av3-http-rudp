import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

LOG_DIR = '/home/lucas/projeto-redes/logs'

def carregar(arquivo, label):
    df = pd.read_csv(arquivo, names=['exec','protocolo','tempo','throughput'])
    print(f"\n=== {label} ===")
    print(f"  Execuções:     {len(df)}")
    print(f"  Mínimo:        {df['throughput'].min():.4f} Mbps")
    print(f"  Máximo:        {df['throughput'].max():.4f} Mbps")
    print(f"  Média:         {df['throughput'].mean():.4f} Mbps")
    print(f"  Desvio Padrão: {df['throughput'].std():.4f} Mbps")
    return df['throughput'].mean(), df['throughput'].std()

tcp_A_mean,  tcp_A_std  = carregar(f'{LOG_DIR}/tcp_cenario_A.csv',  'TCP  Cenário A')
tcp_B_mean,  tcp_B_std  = carregar(f'{LOG_DIR}/tcp_cenario_B.csv',  'TCP  Cenário B')
tcp_C_mean,  tcp_C_std  = carregar(f'{LOG_DIR}/tcp_cenario_C.csv',  'TCP  Cenário C')
rudp_A_mean, rudp_A_std = carregar(f'{LOG_DIR}/rudp_cenario_A.csv', 'RUDP Cenário A')
rudp_B_mean, rudp_B_std = carregar(f'{LOG_DIR}/rudp_cenario_B.csv', 'RUDP Cenário B')
rudp_C_mean, rudp_C_std = carregar(f'{LOG_DIR}/rudp_cenario_C.csv', 'RUDP Cenário C')

cenarios    = ['A (0%/10ms)', 'B (5%/50ms)', 'C (10%/100ms)']
medias_tcp  = [tcp_A_mean,  tcp_B_mean,  tcp_C_mean]
medias_rudp = [rudp_A_mean, rudp_B_mean, rudp_C_mean]
stds_tcp    = [tcp_A_std,   tcp_B_std,   tcp_C_std]
stds_rudp   = [rudp_A_std,  rudp_B_std,  rudp_C_std]

x       = np.arange(len(cenarios))
largura = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - largura/2, medias_tcp,  largura, yerr=stds_tcp,
       label='TCP',   color='steelblue', capsize=5)
ax.bar(x + largura/2, medias_rudp, largura, yerr=stds_rudp,
       label='R-UDP', color='coral',     capsize=5)

ax.set_yscale('log')   
ax.set_xlabel('Cenário de Rede')
ax.set_ylabel('Throughput (Mbps) — escala logarítmica')
ax.set_title('TCP vs R-UDP — Throughput por Cenário (Escala Log)')
ax.set_xticks(x)
ax.set_xticklabels(cenarios)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7, which='both')

for i, (tv, rv) in enumerate(zip(medias_tcp, medias_rudp)):
    ax.text(i - largura/2, tv * 1.3, f'{tv:.2f}', ha='center', fontsize=8, color='navy')
    ax.text(i + largura/2, rv * 1.3, f'{rv:.4f}', ha='center', fontsize=8, color='darkred')

plt.tight_layout()
saida1 = '/home/lucas/projeto-redes/analise/graficos/tcp_vs_rudp_log.png'
plt.savefig(saida1, dpi=150)
print(f"\n✅ Gráfico log salvo em: {saida1}")
plt.close()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

ax1.bar(cenarios, medias_tcp, yerr=stds_tcp,
        color='steelblue', capsize=5)
ax1.set_title('TCP — Throughput por Cenário')
ax1.set_ylabel('Throughput (Mbps)')
ax1.grid(axis='y', linestyle='--', alpha=0.7)
for i, v in enumerate(medias_tcp):
    ax1.text(i, v + stds_tcp[i] + 1, f'{v:.2f}', ha='center', fontsize=9)

ax2.bar(cenarios, medias_rudp, yerr=stds_rudp,
        color='coral', capsize=5)
ax2.set_title('R-UDP — Throughput por Cenário')
ax2.set_ylabel('Throughput (Mbps)')
ax2.grid(axis='y', linestyle='--', alpha=0.7)
for i, v in enumerate(medias_rudp):
    ax2.text(i, v + stds_rudp[i] + 0.01, f'{v:.4f}', ha='center', fontsize=9)

plt.tight_layout()
saida2 = '/home/lucas/projeto-redes/analise/graficos/tcp_vs_rudp_subplots.png'
plt.savefig(saida2, dpi=150)
print(f"✅ Gráfico subplots salvo em: {saida2}")
plt.close()
