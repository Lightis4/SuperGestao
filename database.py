
import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()


class Database:
    TABELAS = {"produtos", "fornecedores", "movimentacoes"}

    def __init__(self):
        self.url = os.getenv("DATABASE_URL")

        if not self.url:
            raise ValueError(
                "Configure DATABASE_URL no arquivo .env"
            )

    @contextmanager
    def conexao(self):
        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=10
        ) as conn:
            yield conn

    def testar(self):
        with self.conexao() as conn:
            return conn.execute(
                "SELECT current_database() AS banco"
            ).fetchone()

    def listar(self, tabela):
        if tabela not in self.TABELAS:
            raise ValueError("Tabela não permitida")

        consulta = sql.SQL(
            "SELECT * FROM {} ORDER BY id DESC"
        ).format(sql.Identifier(tabela))

        with self.conexao() as conn:
            return conn.execute(consulta).fetchall()

    def inserir(self, tabela, dados):
        if tabela not in {"produtos", "fornecedores"}:
            raise ValueError("Tabela não permitida")

        colunas = list(dados.keys())

        consulta = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({}) RETURNING *"
        ).format(
            sql.Identifier(tabela),
            sql.SQL(", ").join(
                sql.Identifier(c) for c in colunas
            ),
            sql.SQL(", ").join(
                sql.Placeholder() for _ in colunas
            )
        )

        with self.conexao() as conn:
            return conn.execute(
                consulta, list(dados.values())
            ).fetchone()

    def atualizar(self, tabela, registro_id, dados):
        if tabela not in {"produtos", "fornecedores"}:
            raise ValueError("Tabela não permitida")

        campos = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(
                sql.Identifier(c),
                sql.Placeholder()
            )
            for c in dados
        )

        consulta = sql.SQL(
            "UPDATE {} SET {} WHERE id = %s RETURNING *"
        ).format(sql.Identifier(tabela), campos)

        parametros = list(dados.values()) + [registro_id]

        with self.conexao() as conn:
            return conn.execute(
                consulta, parametros
            ).fetchone()

    def excluir(self, tabela, registro_id):
        if tabela not in {"produtos", "fornecedores"}:
            raise ValueError("Tabela não permitida")

        consulta = sql.SQL(
            "DELETE FROM {} WHERE id = %s RETURNING id"
        ).format(sql.Identifier(tabela))

        with self.conexao() as conn:
            return conn.execute(
                consulta, (registro_id,)
            ).fetchone()

    def movimentar(self, tipo, produto_id, quantidade, valor):
        with self.conexao() as conn:
            resultado = conn.execute(
                """
                SELECT registrar_movimentacao(
                    %s, %s, %s, %s
                ) AS id
                """,
                (tipo, produto_id, quantidade, valor)
            ).fetchone()

            return resultado["id"]
