# Endpoint de placa - Demo Renault

API fictícia para a demo do agente de recuperação de código de rádio. Não há autenticação nem dados reais.

## Placas da demo

| Placa   | Status         | Resposta                                                   |
|---------|----------------|------------------------------------------------------------|
| FSC1D23 | disponivel     | `{"placa":"FSC1D23","status":"disponivel","codigo":"3847"}` |
| FSC1D24 | bloqueado      | `{"placa":"FSC1D24","status":"bloqueado"}`                 |
| FSC1D25 | nao_localizado | `{"placa":"FSC1D25","status":"nao_localizado"}`            |

## Modo tolerante (só para a demo)

O reconhecimento de voz costuma entregar a placa incompleta ou com o final cortado. O endpoint aceita isso:

1. **Placa exata:** usa a própria placa.
2. **Começa com pelo menos duas das letras F, S, C** (nos quatro primeiros caracteres): escolhe a placa da demo pelo **último caractere** enviado, `3`, `4` ou `5`. Sem um final entendido, usa a FSC1D23.
3. **Qualquer outra coisa:** `nao_localizado`, devolvendo o que foi enviado.

A resposta traz sempre a placa completa da demo no campo `placa`, para o agente confirmar em voz alta.

| Enviado | Resposta |
|---|---|
| `FSCD3` | `FSC1D23`, disponivel |
| `FSCD4` | `FSC1D24`, bloqueado |
| `FSCD5` | `FSC1D25`, nao_localizado |
| `FSCD`, `FSC1D2`, `FSC` | `FSC1D23`, disponivel (final não entendido) |
| `ABC1D23`, `XYZ9` | nao_localizado |

A placa aceita minúsculas, hífen e espaços (`fsc-1d23` vira `FSC1D23`). Em produção a placa precisa vir completa: esse modo não existe na API real.

## Endpoints

- `GET /placa/<placa>`: devolve o status da placa.
- `GET /health`: usado pelo Render para checar o serviço.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
curl http://localhost:8000/placa/FSC1D23
curl http://localhost:8000/placa/FSCD4
curl http://localhost:8000/placa/ABC1D23
```

## Deploy no Render

1. Suba esta pasta para um repositório no Git.
2. No Render, crie um Blueprint apontando para o repositório. O `render.yaml` já define o serviço.
3. Depois do deploy, teste: `curl https://<seu-servico>.onrender.com/placa/FSC1D23`.

No plano gratuito o serviço pode ser suspenso por inatividade, e a primeira chamada demora. Chame `/health` alguns minutos antes da demo.
