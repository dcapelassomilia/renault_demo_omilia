import re

from flask import Flask, jsonify

app = Flask(__name__)

# Dados fictícios da demo Renault.
# A 3ª letra da placa decide o cenário. O resto da placa é igual nas três.
PLACAS = {
    "FSC1D23": {"status": "disponivel", "codigo": "3847"},
    "FSB1D23": {"status": "bloqueado"},
    "FSN1D23": {"status": "nao_localizado"},
}
TERCEIRA_LETRA = {"C": "FSC1D23", "B": "FSB1D23", "N": "FSN1D23"}
PADRAO = "FSC1D23"  # usada quando a 3ª letra não foi entendida

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


def resolver(entrada: str):
    """Devolve (placa, dados). Tolerante a placas incompletas, só para a demo.

    1. Placa exata: usa a própria placa.
    2. Uma das duas primeiras letras é F ou S: a 3ª letra (C, B ou N), procurada
       nos quatro primeiros caracteres, escolhe a placa da demo. O final da placa
       não importa. Sem a 3ª letra entendida, usa a placa padrão (disponível).
    3. Qualquer outra coisa: nao_localizado, devolvendo o que foi enviado.
    """
    chave = normalizar(entrada)
    if chave in PLACAS:
        return chave, PLACAS[chave]
    if any(c in chave[:3] for c in "FS"):
        letra = next((c for c in chave[:4] if c in TERCEIRA_LETRA), None)
        placa = TERCEIRA_LETRA.get(letra, PADRAO)
        return placa, PLACAS[placa]
    return chave, {"status": "nao_localizado"}


@app.get("/placa/<placa>")
def consultar_placa(placa):
    resolvida, dados = resolver(placa)
    resposta = {"placa": resolvida, "placa_falada": falar(resolvida), **dados}
    if "codigo" in dados:
        resposta["codigo_falado"] = falar(dados["codigo"])
    return jsonify(resposta)


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
