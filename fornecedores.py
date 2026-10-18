
class Fornecedor:
    def __init__(self, nome, telefone="", email=""):
        self.nome = nome.strip()
        self.telefone = telefone.strip()
        self.email = email.strip()

        if not self.nome:
            raise ValueError("Informe o nome do fornecedor")

    def dados(self):
        return {
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email
        }


class FornecedorService:
    def __init__(self, db):
        self.db = db

    def listar(self):
        return self.db.listar("fornecedores")

    def cadastrar(self, fornecedor):
        return self.db.inserir(
            "fornecedores", fornecedor.dados()
        )

    def editar(self, id_fornecedor, fornecedor):
        return self.db.atualizar(
            "fornecedores",
            id_fornecedor,
            fornecedor.dados()
        )

    def excluir(self, id_fornecedor):
        return self.db.excluir(
            "fornecedores", id_fornecedor
        )
