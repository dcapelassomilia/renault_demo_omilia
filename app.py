import re

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

# Pausas: vírgula entre letras, ponto ao redor dos números (para a voz não
# acelerar nos números). Para voltar ao ritmo anterior, use ", " nos dois.
SEP_LETRAS = ", "
SEP_NUMEROS = ". "


def normalizar(placa: str) -> str:
    """Deixa só letras e números, em maiúsculas (aceita 'fsc-1d23', 'FSC 1D23' etc.)."""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


def falar(texto: str) -> str:
    """'FSC1D23' -> 'éfi, éssi, cê. um. dê. dois. três' (pronto para o agente falar)."""
    if not texto:
        return ""
    itens = [LETRAS.get(c) or DIGITOS.get(c, c) for c in texto]
    saida = itens[0]
    for anterior, atual, item in zip(texto, texto[1:], itens[1:]):
        numero = anterior.isdigit() or atual.isdigit()
        saida += (SEP_NUMEROS if numero else SEP_LETRAS) + item
    return saida


def modelo_da_placa(chave: str):
    if MERCOSUL.match(chave):
        return "mercosul"
    if ANTIGA.match(chave):
        return "antigo"
    return None


def resolver(entrada: str) -> dict:
    """A placa vem exatamente como o agente capturou (7 caracteres).

    1. Formato inválido (nem Mercosul, nem modelo antigo): status formato_invalido.
    2. Placa da demo (começa com F e S): a 3ª letra decide: C disponível,
       B bloqueado, N não localizado.
    3. Qualquer outra placa válida: nao_localizado.
    A placa devolvida é a que foi enviada, sem conversão.
    """
    chave = normalizar(entrada)
    modelo = modelo_da_placa(chave)
    resposta = {"placa": chave, "placa_falada": falar(chave), "modelo": modelo, "formato_ok": modelo is not None}
    if modelo is None:
        resposta["status"] = "formato_invalido"
        return resposta
    status = "nao_localizado"
    if chave[:2] == "FS":
        status = TERCEIRA_LETRA.get(chave[2], "nao_localizado")
    resposta["status"] = status
    if status == "disponivel":
        resposta["codigo"] = CODIGO
        resposta["codigo_falado"] = ". ".join(DIGITOS[c] for c in CODIGO)
    return resposta


@app.get("/placa/<placa>")
def consultar_placa(placa):
    return jsonify(resolver(placa))


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
