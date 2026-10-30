# 🧭 Planejamento Estratégico com IA

A partir de uma descrição curta do negócio (como funciona, números, desafios e metas), gera um **planejamento estratégico completo**: análise **SWOT**, **estratégias cruzadas (matriz TOWS)**, **OKRs mensuráveis** e um **plano de ação de 90 dias** com área responsável e indicador, além dos riscos do plano. Exporta tudo em Markdown.

## O problema

Pequenas e médias empresas raramente fazem planejamento estratégico: consultoria é cara e montar SWOT, OKRs e plano de ação do zero leva dias de reunião. Sem isso, as metas ficam vagas ("vender mais") e ninguém sabe o que fazer na segunda-feira.

## Como a IA resolve

- **Duas etapas encadeadas:** primeiro o diagnóstico (SWOT + TOWS), depois os OKRs e o plano, que recebem o diagnóstico como contexto. Quebrar em etapas deixa o resultado melhor em modelos locais pequenos.
- Cada etapa devolve JSON **validado por esquema Pydantic** (o Ollama gera direto no formato do esquema), então a tela nunca quebra por texto fora do padrão.
- O prompt exige resultados-chave **mensuráveis** (valor atual → meta) e estratégias específicas do negócio, não conselhos genéricos.
- Roda **100% local**: informação estratégica da empresa não sai da máquina.

## Rodando

Precisa do [Ollama](https://ollama.com) instalado e aberto.

```bash
ollama pull llama3.1:8b
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O formulário já vem preenchido com um exemplo (uma cafeteria em Belém). Para usar outro modelo: `OLLAMA_MODEL=qwen2.5:14b streamlit run app.py`. Modelos maiores escrevem planos mais precisos.

## Estrutura

| Arquivo | O que faz |
|---|---|
| `app.py` | Formulário, esquemas (`Diagnostico`, `Plano`), as duas etapas e a exportação |
| `ia.py` | Chamada ao Ollama com saída estruturada e tratamento de erros |

## Stack

Python · Streamlit · Ollama (Llama 3.1, local, structured outputs) · Pydantic

## Próximos passos

- Acompanhar os OKRs: registrar o valor de cada resultado-chave por semana
- Comparar o plano com o realizado no fim dos 90 dias
