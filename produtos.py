
from decimal import Decimal


class Produto:
    def __init__(
        self, nome, categoria, preco,
        estoque_minimo=5, fornecedor_id=None
    ):
        self.nome = nome.strip()
        self.categoria = categoria.strip()
        self.preco = Decimal(str(preco).replace(",", "."))
        self.estoque_minimo = int(estoque_minimo)
        self.fornecedor_id = fornecedor_id

        if not self.nome:
            raise ValueError("Informe o nome do produto")

        if self.preco < 0:
            raise ValueError("Preço não pode ser negativo")

        if self.estoque_minimo < 0:
            raise ValueError("Estoque mínimo inválido")

    def dados(self):
        return {
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "estoque_minimo": self.estoque_minimo,
            "fornecedor_id": self.fornecedor_id
        }


class ProdutoService:
    def __init__(self, db):
        self.db = db

    def listar(self):
        return self.db.listar("produtos")

    def cadastrar(self, produto):
        dados = produto.dados()
        dados["estoque"] = 0
        return self.db.inserir("produtos", dados)

    def editar(self, id_produto, produto):
        return self.db.atualizar(
            "produtos", id_produto, produto.dados()
        )

    def excluir(self, id_produto):
        return self.db.excluir("produtos", id_produto)
