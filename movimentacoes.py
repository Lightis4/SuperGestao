
from decimal import Decimal


class MovimentacaoService:
    def __init__(self, db):
        self.db = db

    def registrar(self, tipo, produto_id, quantidade, valor):
        if tipo not in ("compra", "venda"):
            raise ValueError("Movimentação inválida")

        quantidade = int(quantidade)
        valor = Decimal(str(valor).replace(",", "."))

        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        if valor < 0:
            raise ValueError("Valor não pode ser negativo")

        return self.db.movimentar(
            tipo,
            int(produto_id),
            quantidade,
            valor
        )

    def listar(self):
        return self.db.listar("movimentacoes")
