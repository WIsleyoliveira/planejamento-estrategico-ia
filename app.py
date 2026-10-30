"""Planejamento Estratégico com IA: dados do negócio -> SWOT, estratégias cruzadas, OKRs e plano de 90 dias."""

from typing import Literal

import streamlit as st
from pydantic import BaseModel, Field

from ia import ErroIA, extrair


class Swot(BaseModel):
    forcas: list[str]
    fraquezas: list[str]
    oportunidades: list[str]
    ameacas: list[str]


class Estrategia(BaseModel):
    tipo: Literal["FO", "FA", "DO", "DA"] = Field(
        description="FO: usar força para aproveitar oportunidade; FA: usar força contra ameaça; "
        "DO: corrigir fraqueza aproveitando oportunidade; DA: reduzir fraqueza e ameaça"
    )
    estrategia: str


class Diagnostico(BaseModel):
    swot: Swot
    estrategias: list[Estrategia]


class ResultadoChave(BaseModel):
    descricao: str = Field(description="Mensurável, com número e unidade")
    valor_atual: str
    meta: str


class Okr(BaseModel):
    objetivo: str
    resultados_chave: list[ResultadoChave]


class Acao(BaseModel):
    acao: str
    area: str = Field(description="Área responsável, ex.: Comercial, Marketing, Financeiro, Operação")
    semanas: str = Field(description="Janela no plano de 90 dias, ex.: 'Semanas 1-4'")
    indicador: str = Field(description="Como saber que a ação deu certo")


class Plano(BaseModel):
    okrs: list[Okr]
    acoes_90_dias: list[Acao]
    riscos: list[str] = Field(description="O que pode impedir o plano e como mitigar")


INSTRUCOES_DIAGNOSTICO = """Você é consultor de planejamento estratégico para pequenas e médias empresas brasileiras.
Monte a análise SWOT do negócio com base só nos dados recebidos: forças e fraquezas são
internas, oportunidades e ameaças são externas (mercado, concorrência, economia, regulação).
Depois cruze os quadrantes (matriz TOWS) e proponha estratégias concretas, pelo menos uma de
cada tipo. Seja específico para este negócio: nada de conselho genérico."""

INSTRUCOES_PLANO = """Você é consultor de planejamento estratégico. Com base no diagnóstico e nas metas do
negócio, defina de 2 a 3 OKRs para o horizonte informado. Cada resultado-chave precisa ser
mensurável, com valor atual (use os números informados ou 'A medir') e meta. Depois monte um
plano de ação de 90 dias, com ações que movem os resultados-chave, e liste os riscos do plano."""


def plano_em_markdown(empresa: str, d: Diagnostico, p: Plano) -> str:
    s = d.swot
    linhas = [f"# Planejamento estratégico: {empresa}", "", "## SWOT"]
    for titulo, itens in [("Forças", s.forcas), ("Fraquezas", s.fraquezas),
                          ("Oportunidades", s.oportunidades), ("Ameaças", s.ameacas)]:
        linhas += [f"### {titulo}", *[f"- {i}" for i in itens], ""]
    linhas += ["## Estratégias (TOWS)", *[f"- **{e.tipo}**: {e.estrategia}" for e in d.estrategias], "", "## OKRs"]
    for o in p.okrs:
        linhas += [f"### {o.objetivo}", *[f"- {kr.descricao} (de {kr.valor_atual} para {kr.meta})" for kr in o.resultados_chave], ""]
    linhas += ["## Plano de 90 dias", "| Ação | Área | Quando | Indicador |", "|---|---|---|---|"]
    linhas += [f"| {a.acao} | {a.area} | {a.semanas} | {a.indicador} |" for a in p.acoes_90_dias]
    linhas += ["", "## Riscos", *[f"- {r}" for r in p.riscos]]
    return "\n".join(linhas)


st.set_page_config(page_title="Planejamento Estratégico com IA", page_icon="🧭", layout="wide")
st.title("🧭 Planejamento Estratégico com IA")
st.caption("Descreva o negócio e receba SWOT, estratégias cruzadas, OKRs e um plano de 90 dias. Roda local com Ollama.")

with st.form("negocio"):
    c1, c2, c3 = st.columns(3)
    empresa = c1.text_input("Empresa", "Café Aroma do Pará")
    setor = c2.text_input("Setor", "Cafeteria e venda de café especial")
    horizonte = c3.selectbox("Horizonte dos OKRs", ["Próximo trimestre", "Próximo semestre", "Próximo ano"])
    descricao = st.text_area("Como o negócio funciona hoje", height=110,
                             value="Duas lojas em Belém, 9 funcionários. Vende café, salgados e café em grão torrado na casa. "
                                   "Clientes fiéis no bairro, nota 4,8 no Google. Não tem delivery próprio nem loja online.")
    numeros = st.text_area("Números atuais (faturamento, margem, clientes, ticket…)", height=80,
                           value="Faturamento de R$ 95 mil/mês, margem líquida de 8%, ticket médio de R$ 28, "
                                 "40% das vendas no café da manhã, café em grão é 10% do faturamento.")
    desafios = st.text_area("Principais desafios", height=80,
                            value="Aluguel subiu 15%, concorrência de rede grande abrindo perto, movimento fraco à tarde, "
                                  "dono centraliza todas as decisões.")
    metas = st.text_area("Onde quer chegar", height=60,
                         value="Aumentar a margem para 12% e fazer o café em grão virar 25% do faturamento.")
    gerar = st.form_submit_button("Gerar planejamento", type="primary")

if gerar:
    contexto = (f"<negocio>\nEmpresa: {empresa}\nSetor: {setor}\nHoje: {descricao}\nNúmeros: {numeros}\n"
                f"Desafios: {desafios}\nMetas: {metas}\nHorizonte: {horizonte}\n</negocio>")
    try:
        with st.spinner("1/2 · Montando o diagnóstico (SWOT e estratégias)…"):
            diagnostico = extrair(contexto, Diagnostico, INSTRUCOES_DIAGNOSTICO)
        with st.spinner("2/2 · Definindo OKRs e plano de 90 dias…"):
            plano = extrair(f"{contexto}\n\n<diagnostico>\n{diagnostico.model_dump_json()}\n</diagnostico>",
                            Plano, INSTRUCOES_PLANO)
        st.session_state["resultado"] = (empresa, diagnostico, plano)
    except ErroIA as e:
        st.error(str(e))

if resultado := st.session_state.get("resultado"):
    empresa, d, p = resultado
    aba_swot, aba_okr, aba_plano = st.tabs(["SWOT e estratégias", "OKRs", "Plano de 90 dias"])

    with aba_swot:
        quadrantes = [("💪 Forças", d.swot.forcas), ("⚠️ Fraquezas", d.swot.fraquezas),
                      ("🚀 Oportunidades", d.swot.oportunidades), ("🌩️ Ameaças", d.swot.ameacas)]
        for linha in (quadrantes[:2], quadrantes[2:]):
            for coluna, (titulo, itens) in zip(st.columns(2), linha):
                with coluna.container(border=True):
                    st.markdown(f"**{titulo}**\n" + "\n".join(f"- {i}" for i in itens))
        st.markdown("#### Estratégias cruzadas (TOWS)")
        for e in d.estrategias:
            st.markdown(f"**{e.tipo}** · {e.estrategia}")

    with aba_okr:
        for o in p.okrs:
            with st.container(border=True):
                st.markdown(f"**🎯 {o.objetivo}**")
                st.dataframe([kr.model_dump() for kr in o.resultados_chave], use_container_width=True, hide_index=True,
                             column_config={"descricao": "Resultado-chave", "valor_atual": "Hoje", "meta": "Meta"})

    with aba_plano:
        st.dataframe([a.model_dump() for a in p.acoes_90_dias], use_container_width=True, hide_index=True)
        st.markdown("#### Riscos")
        for r in p.riscos:
            st.markdown(f"- {r}")

    st.download_button("Baixar planejamento (.md)", plano_em_markdown(empresa, d, p), "planejamento.md", "text/markdown")
