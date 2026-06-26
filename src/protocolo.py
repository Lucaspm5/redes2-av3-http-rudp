import hashlib
import struct

MATRICULA = "20229030103"   
NOME      = "Lucas Emanuel Pereira Macêdo Silva"

def gerar_auth():
    dados = MATRICULA + NOME
    return hashlib.sha256(dados.encode()).hexdigest()

# Estrutura do cabeçalho R-UDP (binário):
# | seq_num (4 bytes) | ack_num (4 bytes) | flags (1 byte) |
# | checksum (4 bytes) | auth_len (2 bytes) | auth (64 bytes) |
# | data_len (4 bytes) |
# Total fixo: 83 bytes de cabeçalho (79 sem data_len + 4 de data_len)

HEADER_FORMAT = '!IIB I H 64s I'
HEADER_SIZE   = struct.calcsize(HEADER_FORMAT)   

FLAGS_DATA = 0x01
FLAGS_ACK  = 0x02
FLAGS_FIN  = 0x04
FLAGS_SYN  = 0x08

def montar_pacote(seq, ack, flags, dados=b''):
    auth   = gerar_auth().encode()[:64].ljust(64, b'\x00')
    checksum = sum(dados) % (2**32)
    header = struct.pack(
        HEADER_FORMAT,
        seq, ack, flags, checksum,
        len(auth), auth, len(dados)
    )
    return header + dados

def desmontar_pacote(raw):
    h  = struct.unpack(HEADER_FORMAT, raw[:HEADER_SIZE])
    seq, ack, flags, checksum, auth_len, auth, data_len = h
    dados = raw[HEADER_SIZE:HEADER_SIZE + data_len]
    return {
        'seq': seq, 'ack': ack, 'flags': flags,
        'checksum': checksum, 'auth': auth.decode(errors='ignore').strip('\x00'),
        'dados': dados
    }

def verificar_checksum(pacote):
    return sum(pacote['dados']) % (2**32) == pacote['checksum']
