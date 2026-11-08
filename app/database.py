"""Conexão e criação do banco SQLite."""
import os
import sqlite3

# Caminho do arquivo do banco. No Azure App Service fica em /home/tarefas.db
# (pasta /home é o armazenamento persistente do App Service)
DB_PATH = os.getenv("DB_PATH", "tarefas.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conn


def init_db() -> None:
    """Cria a tabela se ela ainda não existir."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tarefas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo      TEXT    NOT NULL,
                descricao   TEXT,
                concluida   INTEGER NOT NULL DEFAULT 0,
                criada_em   TEXT    NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
