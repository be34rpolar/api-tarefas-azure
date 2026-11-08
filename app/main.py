"""API de Tarefas: CRUD simples com FastAPI + SQLite."""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # garante que a tabela existe ao subir a API
    yield


app = FastAPI(
    title="API de Tarefas",
    description="API básica com SQLite hospedada no Azure App Service.",
    version="1.0.0",
    lifespan=lifespan,
)


class TarefaEntrada(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    concluida: bool = False


class Tarefa(TarefaEntrada):
    id: int
    criada_em: str


def _linha_para_tarefa(linha) -> dict:
    tarefa = dict(linha)
    tarefa["concluida"] = bool(tarefa["concluida"])
    return tarefa


@app.get("/health", tags=["Status"])
def health():
    """Usado para verificar se a API está no ar."""
    return {"status": "ok"}


@app.get("/tarefas", response_model=list[Tarefa], tags=["Tarefas"])
def listar_tarefas():
    with get_connection() as conn:
        linhas = conn.execute("SELECT * FROM tarefas ORDER BY id").fetchall()
    return [_linha_para_tarefa(l) for l in linhas]


@app.get("/tarefas/{tarefa_id}", response_model=Tarefa, tags=["Tarefas"])
def buscar_tarefa(tarefa_id: int):
    with get_connection() as conn:
        linha = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return _linha_para_tarefa(linha)


@app.post("/tarefas", response_model=Tarefa, status_code=201, tags=["Tarefas"])
def criar_tarefa(dados: TarefaEntrada):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tarefas (titulo, descricao, concluida) VALUES (?, ?, ?)",
            (dados.titulo, dados.descricao, int(dados.concluida)),
        )
        linha = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _linha_para_tarefa(linha)


@app.put("/tarefas/{tarefa_id}", response_model=Tarefa, tags=["Tarefas"])
def atualizar_tarefa(tarefa_id: int, dados: TarefaEntrada):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tarefas SET titulo = ?, descricao = ?, concluida = ? WHERE id = ?",
            (dados.titulo, dados.descricao, int(dados.concluida), tarefa_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        linha = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
    return _linha_para_tarefa(linha)


@app.delete("/tarefas/{tarefa_id}", status_code=204, tags=["Tarefas"])
def remover_tarefa(tarefa_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
