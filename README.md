# API de Tarefas — FastAPI + SQLite no Azure App Service

API REST básica para cadastrar tarefas, com banco **SQLite**, hospedada de ponta a ponta no **Azure App Service (plano F1, gratuito)**.

- **URL da API:** https://api-tarefas-noah567256.azurewebsites.net
- **Documentação interativa (Swagger):** https://api-tarefas-noah567256.azurewebsites.net/docs

Aluno: Noah Nascimento · RM 567256

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework da API | FastAPI + Pydantic |
| Servidor de aplicação | Uvicorn |
| Banco de dados | SQLite (arquivo `/home/tarefas.db`) |
| Nuvem | Microsoft Azure App Service, Linux, plano F1 (Free), região East US |
| Implantação | Azure Cloud Shell + Azure CLI (`az webapp up`) |

## Arquitetura

![Arquitetura](docs/diagramas/arquitetura.png)

O usuário acessa a URL `*.azurewebsites.net` por HTTPS. O front-end do App Service cuida do certificado TLS e repassa a requisição para o contêiner Linux onde o Uvicorn roda a API FastAPI na porta 8000. A API grava e lê os dados no arquivo SQLite que fica em `/home`, a área de armazenamento persistente do App Service.

## Recursos de nuvem

| Recurso | Configuração |
|---|---|
| Resource Group | `rg-api-tarefas` |
| Região | East US |
| App Service Plan | SKU **F1 (Free)**, Linux: 1 GB de memória, 1 GB de armazenamento, 60 min de CPU/dia |
| Web App | `api-tarefas-noah567256`, Python 3.12 |
| Startup command | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Variável de ambiente | `DB_PATH=/home/tarefas.db` |

## Banco de dados

![Modelo do banco](docs/diagramas/banco.png)

## Fluxo de uma requisição

![Fluxo de requisição](docs/diagramas/requisicao.png)

## Endpoints

| Método | Rota | Descrição | Resposta |
|---|---|---|---|
| GET | `/health` | Verifica se a API está no ar | 200 |
| GET | `/tarefas` | Lista todas as tarefas | 200 |
| GET | `/tarefas/{id}` | Busca uma tarefa | 200 / 404 |
| POST | `/tarefas` | Cria uma tarefa | 201 / 422 |
| PUT | `/tarefas/{id}` | Atualiza uma tarefa | 200 / 404 |
| DELETE | `/tarefas/{id}` | Remove uma tarefa | 204 / 404 |

Exemplo de corpo para POST/PUT:

```json
{ "titulo": "Estudar Azure", "descricao": "Trabalho de Cloud Security", "concluida": false }
```

## Implantação no Azure (Cloud Shell)

![Fluxo de implantação](docs/diagramas/implantacao.png)

```bash
# 1. Resource Group
az group create --name rg-api-tarefas --location eastus

# 2. Código
git clone https://github.com/be34rpolar/api-tarefas-azure.git
cd api-tarefas-azure

# 3. Cria o plano F1 + Web App e publica o código
APP=api-tarefas-noah567256
az webapp up --name $APP --resource-group rg-api-tarefas --runtime "PYTHON:3.12" --sku F1 --location eastus

# 4. Comando de inicialização e caminho do banco
az webapp config set -g rg-api-tarefas -n $APP --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
az webapp config appsettings set -g rg-api-tarefas -n $APP --settings DB_PATH=/home/tarefas.db
az webapp restart -g rg-api-tarefas -n $APP
```

> A assinatura Azure for Students só permite algumas regiões. Para ver quais:
> `az policy assignment list --query "[].parameters.listOfAllowedLocations.value" -o tsv`

Para remover tudo depois: `az group delete --name rg-api-tarefas --yes`

## Rodar localmente

```bash
python3 -m venv venv
source venv/bin/activate        # no Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/docs`. Testes: `pip install pytest httpx && pytest`

## Estrutura do projeto

```
api-tarefas-azure/
├── app/
│   ├── main.py            # rotas da API
│   └── database.py        # conexão e criação da tabela SQLite
├── tests/test_api.py      # testes automatizados
├── docs/diagramas/        # diagramas (fonte .mmd e imagem .png)
├── deploy/                # alternativa: implantação em VM Linux com Nginx (não usada nesta entrega)
└── requirements.txt
```
