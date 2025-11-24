import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Função Dummy para teste de deployment.
    Esta função deve retornar 200 OK se o runtime Python estiver carregando corretamente.
    """
    return func.HttpResponse(
        "Azure Function App is running successfully (Dummy Test).",
        status_code=200
    )