import re
import unicodedata

from flask import Flask, jsonify

app = Flask(__name__)

# Dados fictícios da demo Renault.
# Placa da demo: começa com F e S, e a 3ª letra decide o status. O resto não importa.
TERCEIRA_LETRA = {"C": "disponivel", "B": "bloqueado", "N": "nao_localizado"}
CODIGO = "3847"

MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")  # ABC1D23
ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")              # ABC1234

# Como cada caractere é falado (nomes das letras em português do Brasil).
LETRAS = {
    "A": "á", "B": "bê", "C": "cê", "D": "dê", "E": "é", "F": "éfi", "G": "gê",
    "H": "agá", "I": "i", "J": "jota", "K": "cá", "L": "éli", "M": "ême",
    "N": "êni", "O": "ó", "P": "pê", "Q": "quê", "R": "érri", "S": "éssi",
    "T": "tê", "U": "u", "V": "vê", "W": "dáblio", "X": "xis", "Y": "ípsilon",
    "Z": "zê",
}
DIGITOS = {
    "0": "zero", "1": "um", "2": "dois", "3": "três", "4": "quatro",
    "5": "cinco", "6": "seis", "7": "sete", "8": "oito", "9": "nove",
}
NUMEROS_POR_EXTENSO = {v: k for k, v in DIGITOS.items()}
NUMEROS_POR_EXTENSO.update({"tres": "3"})

# Pausas: vírgula entre letras, ponto ao redor dos números (para a voz não
# acelerar nos números). Para voltar ao ritmo anterior, use ", " nos dois.
SEP_LETRAS = ", "
SEP_NUMEROS = ". "


def sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def normalizar(placa: str) -> str:
    """Deixa só letras e números, em maiúsculas (aceita 'fsc-1d23', 'FSC 1D23' etc.)."""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


def modelo_da_placa(chave: str):
    if MERCOSUL.match(chave):
        return "mercosul"
    if ANTIGA.match(chave):
        return "antigo"
    return None


def status_da_placa(chave: str) -> str:
    if chave[:2] == "FS":
        return TERCEIRA_LETRA.get(chave[2], "nao_localizado")
    return "nao_localizado"


def falar(texto: str) -> str:
    """'FSC1D23' -> 'éfi, éssi, cê. um. dê. dois. três' (versão v5, sem palavras)."""
    return falar_itens([(c, None) for c in texto])


def falar_itens(itens) -> str:
    """Lista de (caractere, palavra) -> 'éfi de faca, éssi de sapo, cê de casa. um. dê de dado. dois. três'."""
    if not itens:
        return ""
    partes = []
    for c, palavra in itens:
        if c.isdigit():
            partes.append(DIGITOS[c])
        else:
            nome = LETRAS.get(c, c)
            partes.append(f"{nome} de {palavra}" if palavra else nome)
    saida = partes[0]
    for (ant, _), (atual, _), parte in zip(itens, itens[1:], partes[1:]):
        numero = ant.isdigit() or atual.isdigit()
        saida += (SEP_NUMEROS if numero else SEP_LETRAS) + parte
    return saida


def ler_itens(texto: str):
    """Lê os itens enviados pelo agente, separados por vírgula.

    - 'F:faca'  -> letra com palavra de apoio. A letra é a PRIMEIRA LETRA DA PALAVRA
                   (a palavra de apoio é a fonte da verdade): 'I:elefante' vira E.
    - 'F'       -> letra sem palavra de apoio: vale a letra dita.
    - '1'/'um'  -> número.
    - 'elefante'-> só a palavra: vale a primeira letra.
    Devolve (itens, ajustes), onde itens é uma lista de (caractere, palavra ou None).
    """
    itens, ajustes = [], []
    for bruto in texto.split(","):
        token = bruto.strip()
        if not token:
            continue
        if ":" in token:
            ouvida, palavra = (parte.strip() for parte in token.split(":", 1))
            palavra_limpa = re.sub(r"[^A-Za-z]", "", sem_acento(palavra))
            if palavra_limpa:
                letra = palavra_limpa[0].upper()
                ouvida_limpa = re.sub(r"[^A-Za-z0-9]", "", ouvida).upper()
                if ouvida_limpa and ouvida_limpa != letra:
                    ajustes.append(f"{ouvida_limpa} -> {letra} ({palavra})")
                itens.append((letra, palavra))
                continue
            token = ouvida
        simples = sem_acento(token).lower()
        if simples in NUMEROS_POR_EXTENSO:
            itens.append((NUMEROS_POR_EXTENSO[simples], None))
        elif re.fullmatch(r"[0-9]+", simples):
            itens.extend((d, None) for d in simples)
        elif re.fullmatch(r"[a-z]", simples):
            itens.append((simples.upper(), None))
        elif re.fullmatch(r"[a-z]+", simples):
            itens.append((simples[0].upper(), token))
        else:
            for c in re.sub(r"[^A-Za-z0-9]", "", simples).upper():
                itens.append((c, None))
    return itens, ajustes


def montar_resposta(chave: str, placa_falada: str, extra=None) -> dict:
    modelo = modelo_da_placa(chave)
    resposta = {"placa": chave, "placa_falada": placa_falada, "modelo": modelo, "formato_ok": modelo is not None}
    resposta.update(extra or {})
    if modelo is None:
        resposta["status"] = "formato_invalido"
        return resposta
    status = status_da_placa(chave)
    resposta["status"] = status
    if status == "disponivel":
        resposta["codigo"] = CODIGO
        resposta["codigo_falado"] = ". ".join(DIGITOS[c] for c in CODIGO)
    return resposta


# ---- v5: recebe a placa já pronta, por exemplo FSC1D23 ----
@app.get("/placa/<placa>")
def consultar_placa_v5(placa):
    chave = normalizar(placa)
    return jsonify(montar_resposta(chave, falar(chave)))


# ---- v6: recebe cada letra com a palavra de apoio, por exemplo F:faca,S:sapo,C:casa,1,D:dado,2,3 ----
@app.get("/v6/placa/<itens>")
def consultar_placa_v6(itens):
    lista, ajustes = ler_itens(itens)
    chave = "".join(c for c, _ in lista)
    return jsonify(montar_resposta(chave, falar_itens(lista), {"ajustes": ajustes}))


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
