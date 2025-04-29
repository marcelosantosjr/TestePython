import streamlit as st
from azure.storage.blob import BlobserviceClient
import os
import pymysql
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

blobConnectionString = os.getenv ('BLOB_CONNECTION_STRING')
blobContainerName = os.getenv ('BLOB_CONTAINER_NAME')
blobaccountName = os.getenv('BLOB_ACCOUNT_NAME')

SQL_SERVER = os.getenv ('SQL_SERVER')
SQL_DATABASE = os.getenv ('SQL_DATABASE')
SQL_USER = os.getenv ('SQL_USER')
SQL_PASSWORD = os.getenv ('SQL_PASSWORD')

st.title('Cadastro de Produtos')

#Formulário cadastro de produtos
product_name = st.text_input('Nome do Produto')
product_price = st.number_input('Preço do Produto', min_value=0.0, format='%2f')
product_description = st.text_area('Descrição do Produto')
product_image = st.file_upLoader ('Imagem do Produto', type=['jpg', 'png', 'jpeg'])

#Save image on blobo storage
def upload_blob(file):
    blob_service_client = BlobserviceClient.from_connection_string(blobConnectionString)
    container_client = blob_service_client.get_container_client(blobContainerName)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwirite=True)
    image_url = f"https://{blobaccountName}.blob.core.windows.net/{blobContainerName}/{blob_name}"
    return image_url

def insert_product (product_name, product_price, product_description, product_image):
   try:
    conn = pymssql.connect(server=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO Produtos (nome, preco, descricao, imagem_url) VALUES ('{product_name}', {product_price}, '{product_description}', '{product_image}')")
    conn.commit()
    conn.close()

    return True
   except Exception as e:
      st.error(f'Erro ao inserir: {e}')
      return False


if st.button('Salvar Produto'):
    if product_image is not None:
        image_url = upload_blob(product_image)
        insert_product(product_name, product_price, product_description, image_url)
    return_message = 'Produto salvo com sucesso'

st.header('Produtos Cadastrados')

if st.button('Listar Produtos'):
    try:
        conn = pymssql.connect(server=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produtos")
        produtos = cursor.fetchall()
        conn.close()

        for produto in produtos:
            st.image(produto[4], width=100)
            st.write(f"Nome: {produto[1]}")
            st.write(f"Preço: {produto[2]}")
            st.write(f"Descrição: {produto[3]}")
            st.write("---")

    except Exception as e:
        st.error(f'Erro ao listar produtos: {e}')
    return_message = 'Produtos listados com sucesso'
