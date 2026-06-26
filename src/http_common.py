import os, hashlib

WWW_DIR = '/app/www'
MATRICULA = "20229030103"
NOME = "Lucas Emanuel Pereira Macedo Silva"

def gerar_auth():
    return hashlib.sha256((MATRICULA + NOME).encode()).hexdigest()

def montar_requisicao(caminho, host):
    linha = f"GET {caminho} HTTP/1.1\r\n"
    headers = f"Host: {host}\r\nX-Custom-Auth: {gerar_auth()}\r\n\r\n"
    return (linha + headers).encode()

def parsear_requisicao(dados: bytes):
    texto = dados.decode(errors='ignore')
    linhas = texto.split('\r\n')
    partes = linhas[0].split()
    metodo, caminho = partes[0], partes[1]
    return metodo, caminho

CONTENT_TYPES = {
    '.html': 'text/html',
    '.bin':  'application/octet-stream',
    '.txt':  'text/plain',
}

def montar_resposta(caminho):
    caminho_arquivo = os.path.join(WWW_DIR, caminho.lstrip('/'))
    if os.path.isfile(caminho_arquivo):
        with open(caminho_arquivo, 'rb') as f:
            corpo = f.read()
        ext = os.path.splitext(caminho_arquivo)[1]
        ctype = CONTENT_TYPES.get(ext, 'application/octet-stream')
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {ctype}\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {gerar_auth()}\r\n"
            "\r\n"
        ).encode()
        return header + corpo
    else:
        corpo = b"<html><body><h1>404 Not Found</h1></body></html>"
        header = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {gerar_auth()}\r\n"
            "\r\n"
        ).encode()
        return header + corpo
