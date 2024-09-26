# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import requests, os, uuid, json
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return traduzir()  # Função que você criou para traduzir o texto
    return render_template('index.html')

# Variáveis de ambiente e headers globais para a API de tradução
key = os.environ['KEY']
endpoint = os.environ['ENDPOINT']
location = os.environ['LOCATION']

# Cabeçalhos para a API
headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

# Dicionário de mapeamento de códigos de idioma para nomes
language_names = {
    'pt': 'Português',
    'en': 'Inglês',
    'it': 'Italiano',
    'ja': 'Japonês',
    'ru': 'Russo',
    'de': 'Alemão',
    # Adicione mais mapeamentos conforme necessário
}

def detect_language(texto): 
    # Detecta o idioma do texto fornecido
    path = '/detect?api-version=3.0'
    constructed_url = endpoint + path

    body = [{'text': texto}]  # Texto a ser detectado

    # Faz a requisição para a API
    response = requests.post(constructed_url, headers=headers, json=body).json()

    # Acessa o idioma detectado
    detected_language = response[0]['language']

    # Retorna o nome do idioma detectado ou 'Idioma não identificado'
    detected_language_name = language_names.get(detected_language, 'Idioma não identificado')

    return detected_language, detected_language_name

@app.route('/', methods=['POST'])
def traduzir():
    # Lê o texto e o idioma de destino do formulário
    original_text = request.form['text']
    target_language = request.form['language']

    # Detecta o idioma original do texto
    detected_language, detected_language_name = detect_language(original_text)
    # print(f"Idioma detectado: {detected_language_name}")

    # Prepara a URL para a tradução
    path = '/translate?api-version=3.0'
    params = f'&from={detected_language}&to={target_language}'
    constructed_url = endpoint + path + params

    # Corpo da requisição com o texto original
    body = [{'text': original_text}]

    # Faz a requisição para a API de tradução
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    translator_response = translator_request.json()

    # Acessa o texto traduzido corretamente
    translated_text = translator_response[0]['translations'][0]['text']

    # Renderiza o template de resultados
    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language,
        detected_language_name=detected_language_name  # Nome do idioma detectado
    )

if __name__ == '__main__':
    app.run(debug=True)
