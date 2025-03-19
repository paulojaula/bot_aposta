import nltk
nltk.download('all')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import mysql.connector
import os
import time

# Exibe a imagem super_bet.gif com largura ajustada
col1, col2 = st.columns(2)
with col1:
    st.image("super_bet.gif", width=750)

@st.cache_data
def ler_dados_mysql():
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
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
    start_time = time.time()
    texto = texto.lower()
    tokens = word_tokenize(texto)
    tokens = [token for token in tokens if token.isalnum()]
    tokens = [token for token in tokens if token not in stopwords.words('portuguese')]
    execution
