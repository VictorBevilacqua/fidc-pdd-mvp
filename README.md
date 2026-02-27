# FIDC Checklist MVP

MVP para automatizar a extração de informações públicas (XML do FNET/CVM) e gerar um checklist básico de alerta para FIDCs.

## O que este MVP faz
- Lê 1 arquivo XML do informe (mensal/trimestral)
- Extrai tabelas (quando identificadas)
- Calcula KPIs básicos (ex.: vencidos vs a vencer, concentração em >180 dias)
- Gera um Excel com:
  - KPIs
  - Checklist (OK/ALERTA)
  - Tabelas extraídas

## Como rodar
1) Criar ambiente e instalar dependências:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
