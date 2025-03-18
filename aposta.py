import nltk
nltk.download('all')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import mysql.connector
import os

# Exibe a imagem super_bet.gif com largura ajustada
col1, col2 = st.columns(2)  # Cria duas colunas
with col1:
    st.image("super_bet.gif", width=750)  # Aumenta o tamanho do GIF para 750 pixels

@st.cache_data
def ler_dados_mysql():
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",  # Tenta conectar usando 127.0.0.1
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DATABASE")
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT pergunta, resposta FROM perguntas_respostas")
        resultados = mycursor.fetchall()
        dados = {pergunta: resposta for pergunta, resposta in resultados}
        mydb.close()
        return dados
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao MySQL: {err}")
        return {}

@st.cache_data
def preprocessar_texto(texto):
    texto = texto.lower()
    tokens = word_tokenize(texto)
    tokens = [token for token in tokens if token.isalnum()]
    tokens = [token for token in tokens if token not in stopwords.words('portuguese')]
    return ' '.join(tokens)

@st.cache_data
def calcular_tfidf_similaridade(perguntas_excel, pergunta_cliente):
    perguntas_preprocessadas = [preprocessar_texto(pergunta) for pergunta in perguntas_excel]
    pergunta_cliente_preprocessada = preprocessar_texto(pergunta_cliente)
    vectorizer = TfidfVectorizer()
    matriz_tfidf = vectorizer.fit_transform(perguntas_preprocessadas + [pergunta_cliente_preprocessada])
    matriz_similaridade = cosine_similarity(matriz_tfidf[-1], matriz_tfidf[:-1])
    return matriz_similaridade

def encontrar_resposta(pergunta_cliente, dados, nome_usuario):
    termos = {
        'handicap': 'Handicap é uma forma de aposta onde uma vantagem ou desvantagem virtual é dada a um time ou jogador antes do início do evento.',
        'aposta': 'Uma aposta é um acordo onde um valor é arriscado em um evento com um resultado incerto.',
        'futebol': 'Futebol é um esporte de equipe jogado entre dois times de onze jogadores com uma bola esférica.',
        # Adicione mais termos e explicações aqui
    }

    pergunta_cliente_lower = pergunta_cliente.lower()
    for termo, explicacao in termos.items():
        if termo in pergunta_cliente_lower:
            return f"{nome_usuario}, {explicacao}"

    if not dados:
        return "Desculpe, não foi possível carregar os dados."

    perguntas_excel = list(dados.keys())
    if not perguntas_excel:  # Verifica se a lista de perguntas está vazia
        return "Não entendi sua pergunta, pode perguntar novamente?"

    matriz_similaridade = calcular_tfidf_similaridade(perguntas_excel, pergunta_cliente)
    indice_melhor_pergunta = matriz_similaridade.argmax()
    melhor_pergunta = perguntas_excel[indice_melhor_pergunta]
    resposta = dados.get(melhor_pergunta)

    # Nova verificação para garantir que a resposta não seja vazia e a similaridade seja alta o suficiente
    if not resposta or matriz_similaridade[0][indice_melhor_pergunta] < 0.2: # Ajuste o valor de 0.2 conforme necessário
        return "Não entendi sua pergunta, pode perguntar novamente?"

    return f"{nome_usuario}, {resposta}"

# Modificando a exibição do Streamlit
# with col2:
st.title("Assistente de Apostas")
if 'nome_usuario' not in st.session_state:
    st.session_state['nome_usuario'] = ""

if not st.session_state['nome_usuario']:
    st.write("Olá, meu nome é Superbet, qual o seu nome?")
    nome_usuario = st.text_input("Qual o seu nome?")
    if nome_usuario:
        st.session_state['nome_usuario'] = nome_usuario
        st.write(f"Boa tarde, {nome_usuario}! Faça sua pergunta ou digite 'sair' para finalizar:")
        pergunta_cliente = st.text_input("")
        st.session_state['pergunta_cliente'] = pergunta_cliente # Armazena a pergunta
else:
    nome_usuario = st.session_state['nome_usuario']
    st.write(f"Boa tarde, {nome_usuario}! Faça sua pergunta ou digite 'sair' para finalizar:")
    pergunta_cliente = st.text_input("", value=st.session_state.get('pergunta_cliente', ''))  # Campo de entrada para a pergunta

    if pergunta_cliente:
        if pergunta_cliente.lower() == 'sair':
            st.write(f"Foi um prazer te ajudar, {nome_usuario}!")
            st.session_state['nome_usuario'] = ""
            for key in st.session_state.keys():
                del st.session_state[key]
            st.empty()
            st.rerun()
        else:
            dados = ler_dados_mysql()
            resposta = encontrar_resposta(per
