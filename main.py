
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal

from database import Database
from produtos import Produto, ProdutoService
from fornecedores import Fornecedor, FornecedorService
from movimentacoes import MovimentacaoService


FUNDO = "#0f172a"
PAINEL = "#1e293b"
AZUL = "#2563eb"
BRANCO = "#f8fafc"


class SuperGestao:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperGestão - Supermercado")
        self.root.geometry("1150x730")
        self.root.minsize(850, 550)
        self.root.configure(bg=FUNDO)

        self.db = Database()
        self.produtos = ProdutoService(self.db)
        self.fornecedores = FornecedorService(self.db)
        self.movimentos = MovimentacaoService(self.db)

        self.produto_id = None
        self.fornecedor_id = None
        self.lista_produtos = []
        self.lista_fornecedores = []

        self.estilo()
        self.montar_interface()
        self.atualizar_tudo()

    def estilo(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TNotebook", background=FUNDO
        )
        style.configure(
            "TNotebook.Tab",
            background=PAINEL,
            foreground=BRANCO,
            padding=(18, 12)
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", AZUL)]
        )
        style.configure(
            "Treeview",
            background=PAINEL,
            foreground=BRANCO,
            fieldbackground=PAINEL,
            rowheight=28
        )
        style.configure(
            "Treeview.Heading",
            background=AZUL,
            foreground=BRANCO,
            font=("Arial", 10, "bold")
        )
        style.map(
            "Treeview",
            background=[("selected", AZUL)]
        )

    def titulo(self, parent, texto):
        tk.Label(
            parent,
            text=texto,
            bg=FUNDO,
            fg=BRANCO,
            font=("Arial", 19, "bold")
        ).pack(pady=18)

    def campo(self, parent, texto, largura=23):
        frame = tk.Frame(parent, bg=FUNDO)
        frame.pack(side="left", padx=7, pady=5)

        tk.Label(
            frame,
            text=texto,
            bg=FUNDO,
            fg=BRANCO
        ).pack(anchor="w")

        entrada = ttk.Entry(frame, width=largura)
        entrada.pack(pady=5)
        return entrada

    def botao(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            command=lambda: self.executar(comando),
            bg=AZUL,
            fg="white",
            relief="flat",
            padx=12,
            pady=8,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )

    def executar(self, funcao):
        try:
            funcao()
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def tabela(self, parent, colunas):
        frame = tk.Frame(parent, bg=FUNDO)
        frame.pack(
            fill="both", expand=True,
            padx=18, pady=12
        )

        tree = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        for coluna in colunas:
            tree.heading(coluna, text=coluna)
            tree.column(
                coluna, width=125, anchor="center"
            )

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )
        tree.configure(yscrollcommand=scroll.set)

        tree.pack(
            side="left", fill="both", expand=True
        )
        scroll.pack(side="right", fill="y")

        return tree

    def preencher(self, tree, registros):
        for item in tree.get_children():
            tree.delete(item)

        for registro in registros:
            tree.insert(
                "", "end", values=registro
            )

    def montar_interface(self):
        topo = tk.Frame(self.root, bg=PAINEL)
        topo.pack(fill="x")

        tk.Label(
            topo,
            text="SUPERGESTÃO",
            bg=PAINEL,
            fg=BRANCO,
            font=("Arial", 22, "bold")
        ).pack(
            side="left", padx=22, pady=16
        )

        self.botao(
            topo, "Atualizar tudo",
            self.atualizar_tudo
        ).pack(side="right", padx=20)

        abas = ttk.Notebook(self.root)
        abas.pack(
            fill="both", expand=True,
            padx=12, pady=12
        )

        self.aba_produtos = tk.Frame(
            abas, bg=FUNDO
        )
        self.aba_fornecedores = tk.Frame(
            abas, bg=FUNDO
        )
        self.aba_movimentos = tk.Frame(
            abas, bg=FUNDO
        )
        self.aba_historico = tk.Frame(
            abas, bg=FUNDO
        )

        abas.add(
            self.aba_produtos,
            text="Produtos / Estoque"
        )
        abas.add(
            self.aba_fornecedores,
            text="Fornecedores"
        )
        abas.add(
            self.aba_movimentos,
            text="Compras / Vendas"
        )
        abas.add(
            self.aba_historico,
            text="Histórico"
        )

        self.criar_produtos()
        self.criar_fornecedores()
        self.criar_movimentos()
        self.criar_historico()

    def criar_produtos(self):
        aba = self.aba_produtos
        self.titulo(aba, "Cadastro de Produtos")

        formulario = tk.Frame(aba, bg=FUNDO)
        formulario.pack()

        self.p_nome = self.campo(
            formulario, "Nome"
        )
        self.p_categoria = self.campo(
            formulario, "Categoria"
        )
        self.p_preco = self.campo(
            formulario, "Preço", 12
        )
        self.p_minimo = self.campo(
            formulario, "Estoque mínimo", 12
        )
        self.p_minimo.insert(0, "5")

        linha = tk.Frame(aba, bg=FUNDO)
        linha.pack(pady=8)

        tk.Label(
            linha,
            text="Fornecedor:",
            bg=FUNDO,
            fg=BRANCO
        ).pack(side="left", padx=5)

        self.p_fornecedor = ttk.Combobox(
            linha,
            state="readonly",
            width=35
        )
        self.p_fornecedor.pack(
            side="left", padx=5
        )

        botoes = tk.Frame(aba, bg=FUNDO)
        botoes.pack(pady=8)

        for texto, comando in [
            ("Cadastrar", self.cadastrar_produto),
            ("Editar", self.editar_produto),
            ("Excluir", self.excluir_produto),
            ("Limpar", self.limpar_produto)
        ]:
            self.botao(
                botoes, texto, comando
            ).pack(side="left", padx=5)

        self.tree_produtos = self.tabela(
            aba,
            (
                "ID", "Nome", "Categoria",
                "Preço", "Estoque",
                "Mínimo", "Fornecedor"
            )
        )

        self.tree_produtos.bind(
            "<<TreeviewSelect>>",
            self.selecionar_produto
        )

    def id_fornecedor_escolhido(self):
        indice = self.p_fornecedor.current()

        if indice <= 0:
            return None

        return self.lista_fornecedores[
            indice - 1
        ]["id"]

    def obter_produto(self):
        return Produto(
            self.p_nome.get(),
            self.p_categoria.get(),
            self.p_preco.get(),
            self.p_minimo.get(),
            self.id_fornecedor_escolhido()
        )

    def cadastrar_produto(self):
        self.produtos.cadastrar(
            self.obter_produto()
        )
        messagebox.showinfo(
            "Sucesso", "Produto cadastrado!"
        )
        self.limpar_produto()
        self.atualizar_tudo()

    def editar_produto(self):
        if self.produto_id is None:
            raise ValueError(
                "Selecione um produto na tabela"
            )

        self.produtos.editar(
            self.produto_id,
            self.obter_produto()
        )

        messagebox.showinfo(
            "Sucesso", "Produto atualizado!"
        )
        self.limpar_produto()
        self.atualizar_tudo()

    def excluir_produto(self):
        if self.produto_id is None:
            raise ValueError(
                "Selecione um produto"
            )

        if messagebox.askyesno(
            "Confirmar", "Excluir este produto?"
        ):
            self.produtos.excluir(
                self.produto_id
            )
            self.limpar_produto()
            self.atualizar_tudo()

    def selecionar_produto(self, evento=None):
        selecao = self.tree_produtos.selection()
        if not selecao:
            return

        valores = self.tree_produtos.item(
            selecao[0], "values"
        )
        self.produto_id = int(valores[0])

        produto = next(
            p for p in self.lista_produtos
            if p["id"] == self.produto_id
        )

        for entrada, valor in [
            (self.p_nome, produto["nome"]),
            (self.p_categoria, produto["categoria"]),
            (self.p_preco, produto["preco"]),
            (
                self.p_minimo,
                produto["estoque_minimo"]
            )
        ]:
            entrada.delete(0, "end")
            entrada.insert(0, str(valor))

        indice = 0

        for i, fornecedor in enumerate(
            self.lista_fornecedores, 1
        ):
            if fornecedor["id"] == produto["fornecedor_id"]:
                indice = i
                break

        self.p_fornecedor.current(indice)

    def limpar_produto(self):
        self.produto_id = None

        for entrada in [
            self.p_nome,
            self.p_categoria,
            self.p_preco,
            self.p_minimo
        ]:
            entrada.delete(0, "end")

        self.p_minimo.insert(0, "5")
        self.p_fornecedor.current(0)

        for item in self.tree_produtos.selection():
            self.tree_produtos.selection_remove(item)

    def criar_fornecedores(self):
        aba = self.aba_fornecedores
        self.titulo(aba, "Cadastro de Fornecedores")

        formulario = tk.Frame(aba, bg=FUNDO)
        formulario.pack()

        self.f_nome = self.campo(
            formulario, "Nome"
        )
        self.f_telefone = self.campo(
            formulario, "Telefone"
        )
        self.f_email = self.campo(
            formulario, "E-mail", 30
        )

        botoes = tk.Frame(aba, bg=FUNDO)
        botoes.pack(pady=12)

        for texto, comando in [
            ("Cadastrar", self.cadastrar_fornecedor),
            ("Editar", self.editar_fornecedor),
            ("Excluir", self.excluir_fornecedor),
            ("Limpar", self.limpar_fornecedor)
        ]:
            self.botao(
                botoes, texto, comando
            ).pack(side="left", padx=5)

        self.tree_fornecedores = self.tabela(
            aba,
            ("ID", "Nome", "Telefone", "E-mail")
        )

        self.tree_fornecedores.bind(
            "<<TreeviewSelect>>",
            self.selecionar_fornecedor
        )

    def obter_fornecedor(self):
        return Fornecedor(
            self.f_nome.get(),
            self.f_telefone.get(),
            self.f_email.get()
        )

    def cadastrar_fornecedor(self):
        self.fornecedores.cadastrar(
            self.obter_fornecedor()
        )
        messagebox.showinfo(
            "Sucesso", "Fornecedor cadastrado!"
        )
        self.limpar_fornecedor()
        self.atualizar_tudo()

    def editar_fornecedor(self):
        if self.fornecedor_id is None:
            raise ValueError(
                "Selecione um fornecedor"
            )

        self.fornecedores.editar(
            self.fornecedor_id,
            self.obter_fornecedor()
        )

        messagebox.showinfo(
            "Sucesso", "Fornecedor atualizado!"
        )
        self.limpar_fornecedor()
        self.atualizar_tudo()

    def excluir_fornecedor(self):
        if self.fornecedor_id is None:
            raise ValueError(
                "Selecione um fornecedor"
            )

        if messagebox.askyesno(
            "Confirmar", "Excluir fornecedor?"
        ):
            self.fornecedores.excluir(
                self.fornecedor_id
            )
            self.limpar_fornecedor()
            self.atualizar_tudo()

    def selecionar_fornecedor(self, evento=None):
        selecao = self.tree_fornecedores.selection()
        if not selecao:
            return

        valores = self.tree_fornecedores.item(
            selecao[0], "values"
        )
        self.fornecedor_id = int(valores[0])

        for entrada, valor in zip(
            [
                self.f_nome,
                self.f_telefone,
                self.f_email
            ],
            valores[1:]
        ):
            entrada.delete(0, "end")
            entrada.insert(0, valor)

    def limpar_fornecedor(self):
        self.fornecedor_id = None

        for entrada in [
            self.f_nome,
            self.f_telefone,
            self.f_email
        ]:
            entrada.delete(0, "end")

        for item in self.tree_fornecedores.selection():
            self.tree_fornecedores.selection_remove(item)

    def criar_movimentos(self):
        aba = self.aba_movimentos
        self.titulo(
            aba, "Registro de Compras e Vendas"
        )

        formulario = tk.Frame(aba, bg=FUNDO)
        formulario.pack(pady=15)

        tk.Label(
            formulario,
            text="Produto",
            bg=FUNDO,
            fg=BRANCO
        ).grid(row=0, column=0, pady=5)

        self.m_produto = ttk.Combobox(
            formulario,
            width=42,
            state="readonly"
        )
        self.m_produto.grid(
            row=1, column=0, padx=10
        )
        self.m_produto.bind(
            "<<ComboboxSelected>>",
            self.preencher_preco
        )

        tk.Label(
            formulario,
            text="Quantidade",
            bg=FUNDO,
            fg=BRANCO
        ).grid(row=0, column=1)

        self.m_quantidade = ttk.Entry(
            formulario, width=15
        )
        self.m_quantidade.grid(
            row=1, column=1, padx=10
        )

        tk.Label(
            formulario,
            text="Valor unitário",
            bg=FUNDO,
            fg=BRANCO
        ).grid(row=0, column=2)

        self.m_valor = ttk.Entry(
            formulario, width=15
        )
        self.m_valor.grid(
            row=1, column=2, padx=10
        )

        botoes = tk.Frame(aba, bg=FUNDO)
        botoes.pack(pady=20)

        self.botao(
            botoes,
            "Registrar Compra",
            lambda: self.registrar("compra")
        ).pack(side="left", padx=10)

        self.botao(
            botoes,
            "Registrar Venda",
            lambda: self.registrar("venda")
        ).pack(side="left", padx=10)

        tk.Label(
            aba,
            text=(
                "Compra: adiciona unidades ao estoque. "
                "Venda: retira unidades do estoque."
            ),
            bg=FUNDO,
            fg=BRANCO,
            font=("Arial", 12)
        ).pack(pady=20)

    def preencher_preco(self, evento=None):
        indice = self.m_produto.current()

        if indice < 0:
            return

        produto = self.lista_produtos[indice]
        self.m_valor.delete(0, "end")
        self.m_valor.insert(
            0, str(produto["preco"])
        )

    def registrar(self, tipo):
        indice = self.m_produto.current()

        if indice < 0:
            raise ValueError(
                "Selecione um produto"
            )

        produto = self.lista_produtos[indice]

        quantidade = int(
            self.m_quantidade.get()
        )
        valor = Decimal(
            self.m_valor.get().replace(",", ".")
        )

        self.movimentos.registrar(
            tipo,
            produto["id"],
            quantidade,
            valor
        )

        messagebox.showinfo(
            "Sucesso",
            f"{tipo.capitalize()} registrada!"
        )

        self.m_quantidade.delete(0, "end")
        self.atualizar_tudo()

    def criar_historico(self):
        aba = self.aba_historico
        self.titulo(
            aba, "Histórico de Compras e Vendas"
        )

        self.botao(
            aba,
            "Atualizar Histórico",
            self.atualizar_historico
        ).pack(pady=10)

        self.tree_historico = self.tabela(
            aba,
            (
                "ID", "Tipo", "Produto",
                "Quantidade", "Valor",
                "Total", "Data"
            )
        )

    def atualizar_historico(self):
        registros = self.movimentos.listar()

        nomes = {
            p["id"]: p["nome"]
            for p in self.lista_produtos
        }

        linhas = []

        for m in registros:
            linhas.append((
                m["id"],
                m["tipo"].capitalize(),
                nomes.get(
                    m["produto_id"], "Produto"
                ),
                m["quantidade"],
                m["valor_unitario"],
                m["total"],
                m["criado_em"].strftime(
                    "%d/%m/%Y %H:%M"
                )
            ))

        self.preencher(
            self.tree_historico, linhas
        )

    def atualizar_tudo(self):
        self.lista_fornecedores = (
            self.fornecedores.listar()
        )
        self.lista_produtos = (
            self.produtos.listar()
        )

        nomes = {
            f["id"]: f["nome"]
            for f in self.lista_fornecedores
        }

        self.p_fornecedor["values"] = [
            "Sem fornecedor"
        ] + [
            f'{f["id"]} - {f["nome"]}'
            for f in self.lista_fornecedores
        ]

        self.p_fornecedor.current(0)

        self.preencher(
            self.tree_fornecedores,
            [
                (
                    f["id"],
                    f["nome"],
                    f["telefone"],
                    f["email"]
                )
                for f in self.lista_fornecedores
            ]
        )

        self.preencher(
            self.tree_produtos,
            [
                (
                    p["id"],
                    p["nome"],
                    p["categoria"],
                    p["preco"],
                    p["estoque"],
                    p["estoque_minimo"],
                    nomes.get(
                        p["fornecedor_id"], "-"
                    )
                )
                for p in self.lista_produtos
            ]
        )

        self.m_produto["values"] = [
            f'{p["id"]} - {p["nome"]} '
            f'(Estoque: {p["estoque"]})'
            for p in self.lista_produtos
        ]
        self.m_produto.set("")

        self.atualizar_historico()


if __name__ == "__main__":
    janela = tk.Tk()

    try:
        app = SuperGestao(janela)
        janela.mainloop()
    except Exception as erro:
        messagebox.showerror(
            "Erro ao iniciar", str(erro)
        )
        janela.destroy()
