"""Testes automatizados da API (rodar com: pytest)."""
import os
import tempfile

# Usa um banco temporário para não sujar o banco real
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "teste.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_fluxo_completo():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}

        criada = client.post("/tarefas", json={"titulo": "Estudar Azure"})
        assert criada.status_code == 201
        tarefa_id = criada.json()["id"]

        assert len(client.get("/tarefas").json()) == 1

        atualizada = client.put(
            f"/tarefas/{tarefa_id}",
            json={"titulo": "Estudar Azure", "concluida": True},
        )
        assert atualizada.json()["concluida"] is True

        assert client.delete(f"/tarefas/{tarefa_id}").status_code == 204
        assert client.get(f"/tarefas/{tarefa_id}").status_code == 404


def test_titulo_obrigatorio():
    with TestClient(app) as client:
        assert client.post("/tarefas", json={"titulo": ""}).status_code == 422
