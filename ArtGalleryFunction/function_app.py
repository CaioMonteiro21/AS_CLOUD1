import azure.functions as func # type: ignore
import json
import logging
import os
import sys

# Importa a biblioteca de conexão do seu DB (MySQL).
# Certifique-se de que 'mysql-connector-python' está no requirements.txt
import mysql.connector 

# Adiciona o diretório atual ao PATH para garantir importações corretas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Obtém a URL base do Blob Storage das variáveis de ambiente configuradas no Azure.
# Se não estiver configurada, usa um placeholder para evitar erros de execução local.
BLOB_STORAGE_URL = os.environ.get("BLOB_STORAGE_URL", "https://PLACEHOLDER.blob.core.windows.net/obras/")

# --- DADOS MOCKADOS (Fallback) ---
# Estes dados são retornados apenas se a conexão com o banco de dados falhar.
# Isso ajuda a diagnosticar se o problema é na Function ou na conexão com o DB.
MOCK_OBRAS = [
    {
        "nome": "Erro de Conexão DB",
        "artista": "Sistema Azure",
        "descricao": "Falha ao conectar ou consultar o DB. Verifique a variável DB_CONNECTION_STRING e as regras de Firewall do MySQL.",
        "caminho_imagem": "venus_botticelli.jpg" # Usa um nome de arquivo padrão
    }
]

# --- CONEXÃO E LEITURA DO BANCO DE DADOS ---

def parse_connection_string(conn_str):
    """
    Analisa a Connection String no formato Azure (key=value;key2=value2) 
    e retorna um dicionário de parâmetros limpo para o conector MySQL.
    """
    params = {}
    if not conn_str:
        return params
        
    for part in conn_str.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            # Normaliza a chave: remove espaços, converte para minúsculas e remove 'name' (ex: HostName -> host)
            cleaned_key = key.strip().lower().replace('name', '')
            params[cleaned_key] = value.strip()
    return params

def get_obras_do_banco():
    """
    Tenta conectar-se ao Azure Database for MySQL - Flexible Server para obter a lista de obras.
    Retorna a lista de obras do banco ou os dados mockados em caso de falha.
    """
    # Obtém a string de conexão das Variáveis de Ambiente do Azure
    DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
    
    if not DB_CONNECTION_STRING:
        logging.warning("DB_CONNECTION_STRING não configurada no Azure. Usando dados mockados.")
        return MOCK_OBRAS

    # Converte a Connection String do Azure em parâmetros utilizáveis
    conn_params = parse_connection_string(DB_CONNECTION_STRING)
    
    try:
        logging.info("Tentando conectar e consultar o banco de dados MySQL...")
        
        # Estabelece a conexão com o MySQL Flexible Server
        conn = mysql.connector.connect(
            host=conn_params.get('host'),
            database=conn_params.get('database'),
            user=conn_params.get('user'),
            password=conn_params.get('password'),
            # O Azure exige SSL por padrão. A biblioteca geralmente lida com isso automaticamente,
            # mas ssl_disabled=False garante que tentaremos usar SSL.
            ssl_disabled=False 
        )
        
        # Cria um cursor que retorna os resultados como dicionários (JSON friendly)
        cursor = conn.cursor(dictionary=True) 
        
        # Executa a consulta SQL na tabela 'obras'
        cursor.execute("SELECT nome, artista, descricao, caminho_imagem FROM obras;") 
        obras_db = cursor.fetchall()

        # Fecha a conexão para liberar recursos
        cursor.close()
        conn.close()
        
        # Se a consulta não retornar nada (tabela vazia), avisa nos logs
        if not obras_db:
             logging.info("Conexão bem-sucedida, mas a tabela 'obras' está vazia. Retornando dados mockados para teste.")
             return MOCK_OBRAS
        
        return obras_db # Retorna a lista real de obras


    except Exception as e:
        # Loga o erro detalhado no Application Insights para depuração
        logging.error(f"Erro crítico ao conectar ou consultar o MySQL: {e}", exc_info=True)
        logging.warning("Falha na conexão real. Usando dados mockados como fallback.")
        return MOCK_OBRAS

# --- LÓGICA DE NEGÓCIO DA FUNÇÃO ---

def montar_galeria(obras_db):
    """
    Processa a lista de obras do banco, adicionando a URL completa da imagem
    com base no Blob Storage configurado.
    """
    galeria = []
    for obra in obras_db:
        # Cria uma cópia do objeto para não alterar o original
        obra_completa = obra.copy()
        
        # Constrói a URL pública completa: URL_BASE + NOME_ARQUIVO
        # Ex: https://minhaconta.blob.core.windows.net/obras/monalisa.jpg
        obra_completa["url_imagem"] = f"{BLOB_STORAGE_URL}{obra['caminho_imagem']}"
        
        # Opcional: Remove o nome do arquivo interno, pois o frontend só precisa da URL final
        if "caminho_imagem" in obra_completa:
             del obra_completa["caminho_imagem"]
             
        galeria.append(obra_completa)
    return galeria

# --- DEFINIÇÃO DO HTTP TRIGGER (PONTO DE ENTRADA) ---

# Define o aplicativo de função com nível de autenticação anônimo (público)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="galeria", methods=["GET"])
def galeria(req: func.HttpRequest) -> func.HttpResponse:
    """
    Função Serverless acionada por HTTP GET.
    Retorna a lista de obras de arte em formato JSON.
    """
    logging.info('Requisição HTTP recebida para o endpoint /api/galeria.')

    try:
        # 1. Busca os dados (MySQL ou Mock)
        obras_do_db = get_obras_do_banco()

        # 2. Processa os dados (Adiciona URLs das imagens)
        dados_galeria = montar_galeria(obras_do_db)

        # 3. Retorna a resposta HTTP 200 com o JSON
        return func.HttpResponse(
            json.dumps(dados_galeria, ensure_ascii=False), # Garante caracteres especiais (acentos)
            mimetype="application/json",
            status_code=200,
            headers={
                # Cabeçalhos CORS para permitir que o Frontend (Static Web App) acesse a API
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Methods": "GET",
                "Content-Type": "application/json; charset=utf-8"
            }
        )

    except Exception as e:
        # Captura erros não tratados e retorna erro 500
        logging.error(f"Erro não tratado ao processar a requisição: {e}", exc_info=True)
        return func.HttpResponse(
             json.dumps({"erro": "Erro interno ao carregar a galeria."}),
             status_code=500,
             mimetype="application/json",
             headers={"Access-Control-Allow-Origin": "*"}
        )