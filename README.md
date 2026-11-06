# Endpoint de placa - Demo Renault

API fictícia para a demo do agente de recuperação de código de rádio. Não há autenticação nem dados reais.

## Placas da demo

| Placa   | Status         | Resposta                                                   |
|---------|----------------|------------------------------------------------------------|
| FSC1D23 | disponivel     | `{"placa":"FSC1D23","status":"disponivel","codigo":"3847"}` |
| FSC1D24 | bloqueado      | `{"placa":"FSC1D24","status":"bloqueado"}`                 |
| FSC1D25 | nao_localizado | `{"placa":"FSC1D25","status":"nao_localizado"}`            |
| Outras  | nao_localizado | `{"placa":"<placa>","status":"nao_localizado"}`            |

A placa aceita minúsculas, hífen e espaços (`fsc-1d23` vira `FSC1D23`).

## Endpoints

- `GET /placa/<placa>`: devolve o status da placa.
- `GET /health`: usado pelo Render para checar o serviço.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
curl http://localhost:8000/placa/FSC1D23
curl http://localhost:8000/placa/FSC1D24
curl http://localhost:8000/placa/FSC1D25
```

## Deploy no Render

1. Suba esta pasta para um repositório no Git.
2. No Render, crie um Blueprint apontando para o repositório. O `render.yaml` já define o serviço.
3. Depois do deploy, teste: `curl https://<seu-servico>.onrender.com/placa/FSC1D23`.

No plano gratuito o serviço pode ser suspenso por inatividade, e a primeira chamada demora. Chame `/health` alguns minutos antes da demo.
