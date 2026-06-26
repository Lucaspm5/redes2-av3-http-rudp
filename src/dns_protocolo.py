import struct, socket

# Formato: ID(2 bytes) + flag(1 byte) + nome(32 bytes) + ip(4 bytes)
DNS_FORMAT = '!HB32s4s'
DNS_SIZE = struct.calcsize(DNS_FORMAT)   # = 39 bytes

FLAG_QUERY              = 0
FLAG_RESPONSE_OK        = 1
FLAG_RESPONSE_NXDOMAIN  = 2

def montar_query(id_consulta, nome):
    nome_b = nome.encode()[:32].ljust(32, b'\x00')
    ip_b = b'\x00\x00\x00\x00'
    return struct.pack(DNS_FORMAT, id_consulta, FLAG_QUERY, nome_b, ip_b)

def montar_resposta(id_consulta, nome, ip=None):
    nome_b = nome.encode()[:32].ljust(32, b'\x00')
    if ip is None:
        flag = FLAG_RESPONSE_NXDOMAIN
        ip_b = b'\x00\x00\x00\x00'
    else:
        flag = FLAG_RESPONSE_OK
        ip_b = socket.inet_aton(ip)
    return struct.pack(DNS_FORMAT, id_consulta, flag, nome_b, ip_b)

def desmontar(raw):
    id_consulta, flag, nome_b, ip_b = struct.unpack(DNS_FORMAT, raw[:DNS_SIZE])
    nome = nome_b.decode(errors='ignore').strip('\x00')
    ip = socket.inet_ntoa(ip_b) if flag == FLAG_RESPONSE_OK else None
    return {'id': id_consulta, 'flag': flag, 'nome': nome, 'ip': ip}
