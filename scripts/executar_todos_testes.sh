#!/bin/bash
set -e

CENARIOS=("a" "b" "c")
PROTOCOLOS=("tcp" "rudp")
ARQUIVOS=("arquivo_100kb.bin" "arquivo_1mb.bin" "arquivo_10mb.bin")
EXECUCOES=10

cd ~/Redes_2_FINAL/docker

for cenario in "${CENARIOS[@]}"; do
  CEN_UPPER=$(echo "$cenario" | tr '[:lower:]' '[:upper:]')
  echo "=========================================="
  echo " CENARIO $CEN_UPPER"
  echo "=========================================="

  docker exec cliente tc qdisc del dev eth0 root 2>/dev/null || true
  docker exec cliente bash /app/scripts/cenario_${cenario}.sh
  docker exec cliente tc qdisc show dev eth0

  for protocolo in "${PROTOCOLOS[@]}"; do
    echo "---- Protocolo: $protocolo ----"

    docker exec servidor pkill -f python3 2>/dev/null || true
    docker exec dns pkill -f python3 2>/dev/null || true
    sleep 1

    docker exec cliente tcpdump -i eth0 -w /app/capturas/cenario_${cenario}_${protocolo}.pcap &
    sleep 1

    docker exec -d dns python3 -u /app/dns_server.py
    sleep 1

    if [ "$protocolo" == "tcp" ]; then
      docker exec -d servidor python3 -u /app/http_server_tcp.py
    else
      docker exec -d servidor python3 -u /app/http_server_rudp.py
    fi
    sleep 1

    for arquivo in "${ARQUIVOS[@]}"; do
      echo "  >> Arquivo: $arquivo"
      docker exec cliente python3 -u /app/cliente_completo.py "$protocolo" "$CEN_UPPER" "/$arquivo" "$EXECUCOES"
    done

    docker exec servidor pkill -f python3 2>/dev/null || true
    docker exec dns pkill -f python3 2>/dev/null || true
    docker exec cliente pkill tcpdump 2>/dev/null || true
    sleep 1
  done

  docker exec cliente tc qdisc del dev eth0 root 2>/dev/null || true
done

echo "=========================================="
echo " TODOS OS TESTES CONCLUIDOS"
echo "=========================================="
