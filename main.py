#Projeto feito em Python 
import streamlit as st
import pandas as pd
from datetime import datetime
from datetime import date
import json

st.set_page_config(
    page_title="Central de Ferramentas",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Central de Ferramentas")

# ---------------- Menu ----------------

st.sidebar.title("Ferramentas")

if st.sidebar.button("📈 Vendas e Comissões", use_container_width=True):
    st.session_state.pagina = "vendas"

if st.sidebar.button("📊 Estoque de Protudos", use_container_width=True):
    st.session_state.pagina = "estoque"

if st.sidebar.button("🧮 Calculadora de Juros", use_container_width=True):
    st.session_state.pagina = "juros"

if st.sidebar.button("🏠 Volte para o Início", use_container_width=True):
    st.session_state.pagina = "inicio"

    # ---------------- Conteudo ----------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"


if st.session_state.pagina == "inicio":

    st.header("Bem-vindo!")

    st.write("Escolha uma ferramenta no menu lateral.")

    st.write("Desenvolvido por Rafael Silva | Python • Streamlit • Pandas 👨‍💻 ")


elif st.session_state.pagina == "vendas":

    st.header("📈 Todas as Vendas")

    # Le a base de dados
    with open("database/vendas.json", "r", encoding="utf-8") as arquivo_vendas:
        dados_vendas = json.load(arquivo_vendas)

    db_vendas = pd.DataFrame(dados_vendas["vendas"])

    st.dataframe(db_vendas)


    st.header("📈 Total de Vendas e Comissões")

    # Faz o calculo das comissões e apresenta na tela
    def calcular_comissao(valor):
        if valor < 100:
            return 0
        elif valor < 500:
            return valor * 0.01
        else:
            return valor * 0.05    
    
    
    db_vendas["comissao"] = db_vendas["valor"].apply(calcular_comissao)
    
    
    resultado = (
        db_vendas.groupby("vendedor")[["valor", "comissao"]]
        .sum()
        .reset_index()
    )

    resultado["valor"] = resultado["valor"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    resultado["comissao"] = resultado["comissao"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.dataframe(resultado,use_container_width=True,hide_index=True)

    st.write("Regras da comissão:")
    st.write("Vendas abaixo de R$100,00 não gera comissão ")
    st.write("Vendas abaixo de R$500,00 gera 1 porcento de comissão")
    st.write("A partir de R$500,00 gera 5 porcento de comissão")



elif st.session_state.pagina == "estoque":

    st.header("📊 Estoque de Protudos")

    # Le a base de dados
    with open("database/estoque.json", "r", encoding="utf-8") as arquivo_estoque:
            dados_estoque = json.load(arquivo_estoque)
    
    db_estoque = pd.DataFrame(dados_estoque["estoque"])
    
    st.dataframe(db_estoque)

        
    # Altera o estoque

    produtos = dados_estoque["estoque"]

    nome_produto = st.selectbox("Selecione o produto:", [produto["descricaoProduto"] for produto in produtos])

    produto_selecionado = next( produto for produto in produtos if produto["descricaoProduto"] == nome_produto)

    codigo = produto_selecionado["codigoProduto"]

    st.write(f"**Estoque atual:** {produto_selecionado['estoque']}")

    tipo_movimentacao = st.selectbox("Tipo de movimentação", ["Entrada", "Saida"])

    quantidade_movimentada = st.number_input("Quantidade", min_value=1, step=1)

    botao_registrar =st.button("Registrar Movimentação")

    if botao_registrar:
        estoque_atual = produto_selecionado["estoque"]


        if tipo_movimentacao == "Entrada":
            produto_selecionado["estoque"] = estoque_atual + quantidade_movimentada

        else:
            if quantidade_movimentada > estoque_atual:
                st.error("Produto sem estoque para essa movimentação")
                st.stop()

            else:
                produto_selecionado["estoque"] = estoque_atual - quantidade_movimentada


        with open ("database/estoque.json", "w", encoding="utf-8") as arquivo_estoque:
                json.dump(dados_estoque, arquivo_estoque, indent=4, ensure_ascii=False)

        try:
            with open("database/movimentacao.json", "r", encoding="utf-8") as arquivo_movimentacao:
                logs = json.load(arquivo_movimentacao)

        except FileNotFoundError:
             logs = {
                 "movimentacoes": []
             }

        movimentacao = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            "codigoProduto": codigo,

            "descricaoProduto":
            produto_selecionado["descricaoProduto"],

            "tipo": tipo_movimentacao,

            "quantidade": quantidade_movimentada,

        }

    
        logs["movimentacoes"].append(movimentacao)

        with open("database/movimentacao.json", "w", encoding="utf-8") as arquivo_movimentacao:
            json.dump(logs, arquivo_movimentacao, indent=4, ensure_ascii=False)

        st.success("Movimentação registrada")


    with open("database/movimentacao.json", "r", encoding="utf-8") as arquivo_movimentacoes:
        dados_movimentacao = json.load(arquivo_movimentacoes)

    db_movimentacao = pd.DataFrame(dados_movimentacao["movimentacoes"])
            
    st.dataframe(db_movimentacao)

elif st.session_state.pagina == "juros":

    st.header("🧮 Calculadora de Juros Simples")

    valor_divida = st.number_input("Digite o valor da dívida:",min_value=0.0,format="%.2f")

    data_vencimento = st.date_input("Digite a data de vencimento:", max_value=date.today())

    data_hoje = date.today()

    dias_atraso = (data_hoje - data_vencimento).days

    if st.button("Calcular juros"):

        if dias_atraso <= 0:
            st.success("O pagamento não está atrasado.")
            st.write(f"Valor original: R$ {valor_divida:.2f}")

        else:
            # 2,5% de juros por dia
            percentual = 0.025

            juros = valor_divida * percentual * dias_atraso
            valor_total = valor_divida + juros

            st.write(f"Dias de atraso: {dias_atraso}")
            st.write(f"Valor original: R$ {valor_divida:.2f}")
            st.write(f"Juros Simples: R$ {juros:.2f}")
            st.write(f"Valor total: R$ {valor_total:.2f}")