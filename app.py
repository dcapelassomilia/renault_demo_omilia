import re

from flask import Flask, jsonify

app = Flask(__name__)

# Dados fictícios da demo Renault. Qualquer placa fora desta tabela retorna "nao_localizado".
PLACAS = {
    "FSC1D23": {"status": "disponivel", "codigo": "3847"},
    "FSC1D24": {"status": "bloqueado"},
    "FSC1D25": {"status": "nao_localizado"},
}


def normalizar(placa: str) -> str:
    """Deixa só letras e números, em maiúsculas (aceita 'fsc-1d23', 'FSC 1D23' etc.)."""
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


@app.get("/placa/<placa>")
def consultar_placa(placa):
    chave = normalizar(placa)
    dados = PLACAS.get(chave, {"status": "nao_localizado"})
    return jsonify({"placa": chave, **dados})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
