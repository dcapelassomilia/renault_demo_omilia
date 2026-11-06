import re

from flask import Flask, jsonify

app = Flask(__name__)

# Dados fictícios da demo Renault.
PLACAS = {
    "FSC1D23": {"status": "disponivel", "codigo": "3847"},
    "FSC1D24": {"status": "bloqueado"},
    "FSC1D25": {"status": "nao_localizado"},
}
PADRAO = "FSC1D23"  # usada quando o final da placa não foi entendido
FINAIS = {"3": "FSC1D23", "4": "FSC1D24", "5": "FSC1D25"}

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


def falar(texto: str, separador: str = ", ") -> str:
    """'FSC1D24' -> 'éfi, éssi, cê, um, dê, dois, quatro' (pronto para o agente falar)."""
    return separador.join(LETRAS.get(c) or DIGITOS.get(c, c) for c in texto)


def normalizar(placa: str) -> str:
    """Deixa só letras e números, em maiúsculas (aceita 'fsc-1d23', 'FSC 1D23' etc.)."""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


def resolver(entrada: str):
    """Devolve (placa, dados). Tolerante a placas incompletas, só para a demo.

    1. Placa exata: usa a própria placa.
    2. Começa com pelo menos duas das letras F, S, C: escolhe a placa da demo pelo
       último caractere (3, 4 ou 5). Sem final entendido, usa a placa padrão.
    3. Qualquer outra coisa: nao_localizado.
    """
    chave = normalizar(entrada)
    if chave in PLACAS:
        return chave, PLACAS[chave]
    if sum(1 for c in "FSC" if c in chave[:4]) >= 2:
        placa = FINAIS.get(chave[-1:], PADRAO)
        return placa, PLACAS[placa]
    return chave, {"status": "nao_localizado"}


@app.get("/placa/<placa>")
def consultar_placa(placa):
    resolvida, dados = resolver(placa)
    resposta = {"placa": resolvida, "placa_falada": falar(resolvida), **dados}
    if "codigo" in dados:
        resposta["codigo_falado"] = falar(dados["codigo"], ". ")
    return jsonify(resposta)


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
