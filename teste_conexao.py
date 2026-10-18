
from database import Database

try:
    db = Database()
    resultado = db.testar()

    print("Conexão com Neon realizada com sucesso!")
    print("Banco conectado:", resultado["banco"])

except Exception as erro:
    print("Erro ao conectar com Neon:")
    print(erro)
