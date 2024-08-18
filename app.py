import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import requests  # Para integração com a API de CEP
import re

class SistemaPedidosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pedidos")
        self.root.geometry("1100x650")

        # Inicialização dos atributos de edição
        self.entry_edit_cliente = None
        self.entry_edit_data = None
        self.entry_edit_descricao = None
        self.entry_edit_quantidade = None
        self.entry_edit_endereco = None

        # Inicializar o banco de dados e adicionar coluna 'endereco' se necessário
        self.inicializar_banco_dados()
        self.adicionar_coluna_endereco()

        # Adicionar o atributo para controlar o modo de edição
        self.edit_mode = False
        self.editing_item = None  # Para armazenar o item atualmente sendo editado

        # Criar os frames
        self.frame_adicionar_cliente = ctk.CTkFrame(root)
        self.frame_adicionar_cliente.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_adicionar_pedido = ctk.CTkFrame(root)
        self.frame_adicionar_pedido.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_exibir_pedidos = ctk.CTkFrame(root)
        self.frame_exibir_pedidos.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Configurar o layout da janela principal
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=3)
        root.grid_columnconfigure(0, weight=1)

        self.criar_widgets()

        # Exibir todos os pedidos ao iniciar o aplicativo
        self.exibir_pedidos()

    def inicializar_banco_dados(self):
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            data_pedido TEXT NOT NULL,
            descricao TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            endereco TEXT,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        )
        ''')

        conn.commit()
        conn.close()

    def adicionar_coluna_endereco(self):
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        try:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN endereco TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe

        conn.close()

    def criar_widgets(self):
        self.criar_frame_adicionar_cliente()
        self.criar_frame_adicionar_pedido()
        self.criar_frame_exibir_pedidos()

    def criar_frame_adicionar_cliente(self):
        # Frame principal para adicionar cliente
        self.entry_nome_cliente = ctk.CTkEntry(self.frame_adicionar_cliente, placeholder_text="Nome do Cliente", width=300)
        self.entry_nome_cliente.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Botão com a mesma largura que a entrada
        self.botao_adicionar_cliente = ctk.CTkButton(self.frame_adicionar_cliente, text="Adicionar Cliente", command=self.adicionar_cliente)
        self.botao_adicionar_cliente.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    
        # Novo frame à direita do frame de adicionar cliente
        self.frame_opcoes_cliente = ctk.CTkFrame(self.frame_adicionar_cliente, border_color="white", border_width=1)
        self.frame_opcoes_cliente.grid(row=0, column=1, rowspan=2, padx=180, pady=25, sticky="nswe")  # Ajustado para expandir horizontalmente e encostar à direita

        # Configurar colunas no frame de opções do cliente para os botões
        self.frame_opcoes_cliente.grid_columnconfigure(0, weight=1)
        self.frame_opcoes_cliente.grid_columnconfigure(1, weight=1)
        self.frame_opcoes_cliente.grid_columnconfigure(2, weight=1)

        # Botões lado a lado
        ctk.CTkButton(self.frame_opcoes_cliente, text="Ver Clientes Cadastrados", command=self.ver_clientes_cadastrados).grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        ctk.CTkButton(self.frame_opcoes_cliente, text="Editar Pedido", command=self.ativar_edicao_pedido).grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        ctk.CTkButton(self.frame_opcoes_cliente, text="Excluir Pedido", command=self.excluir_pedido).grid(row=0, column=2, padx=15, pady=15, sticky="ew")

    def criar_frame_adicionar_pedido(self):
        # Configurar colunas para centralização
        for i in range(5):
            self.frame_adicionar_pedido.grid_columnconfigure(i, weight=1)

        # Configurar linhas para centralização vertical
        self.frame_adicionar_pedido.grid_rowconfigure(0, weight=1)
        self.frame_adicionar_pedido.grid_rowconfigure(1, weight=1)

        self.entry_cliente = ctk.CTkEntry(self.frame_adicionar_pedido, placeholder_text="Cliente")
        self.entry_cliente.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.entry_data_pedido = ctk.CTkEntry(self.frame_adicionar_pedido, placeholder_text="DD/MM/AAAA")
        self.entry_data_pedido.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.entry_descricao = ctk.CTkEntry(self.frame_adicionar_pedido, placeholder_text="Descrição")
        self.entry_descricao.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.entry_quantidade = ctk.CTkEntry(self.frame_adicionar_pedido, placeholder_text="Quantidade")
        self.entry_quantidade.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.entry_endereco = ctk.CTkEntry(self.frame_adicionar_pedido, placeholder_text="Endereço (CEP)")
        self.entry_endereco.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        # Adicionar o botão com margem superior
        ctk.CTkButton(self.frame_adicionar_pedido, text="Adicionar Pedido", command=self.adicionar_pedido).grid(
            row=1, column=0, columnspan=5, pady=(10, 10)  # Ajustar o padding superior e inferior
        )

    def criar_frame_exibir_pedidos(self):
        # Adicionar o texto "Pedidos" acima das barras de pesquisa
        ctk.CTkLabel(self.frame_exibir_pedidos, text="Pedidos").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Adicionar as barras de pesquisa
        self.entry_pesquisa_principal = ctk.CTkEntry(self.frame_exibir_pedidos, placeholder_text="Pesquise por nome, data, descrição, endereço...", corner_radius=12, width=750)
        self.entry_pesquisa_principal.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.entry_pesquisa_principal.bind("<KeyRelease>", self.atualizar_pesquisa)

        self.entry_pesquisa_id = ctk.CTkEntry(self.frame_exibir_pedidos, placeholder_text="Pesquise exclusivamente por ID", corner_radius=12, width=400)
        self.entry_pesquisa_id.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.entry_pesquisa_id.bind("<KeyRelease>", self.atualizar_pesquisa_id)

        # Criação do frame para a Treeview e a Scrollbar
        frame_treeview = ctk.CTkFrame(self.frame_exibir_pedidos)
        frame_treeview.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configurar a Scrollbar
        self.scrollbar_vertical = ctk.CTkScrollbar(frame_treeview, orientation="vertical")
        self.scrollbar_vertical.pack(side="right", fill="y")

        # Criação da Treeview com configurações de largura para as colunas
        self.treeview_pedidos = ttk.Treeview(
            frame_treeview,
            columns=("ID", "Cliente", "Data", "Descrição", "QTD", "Endereço"),
            show='headings',
            yscrollcommand=self.scrollbar_vertical.set
        )

        # Configurar cabeçalhos das colunas
        self.treeview_pedidos.heading("ID", text="ID")
        self.treeview_pedidos.heading("Cliente", text="Cliente")
        self.treeview_pedidos.heading("Data", text="Data")
        self.treeview_pedidos.heading("Descrição", text="Descrição")
        self.treeview_pedidos.heading("QTD", text="QTD")
        self.treeview_pedidos.heading("Endereço", text="Endereço")

        # Configurar larguras das colunas
        self.treeview_pedidos.column("ID", width=40)
        self.treeview_pedidos.column("Cliente", width=100)
        self.treeview_pedidos.column("Data", width=80)
        self.treeview_pedidos.column("Descrição", width=250)
        self.treeview_pedidos.column("QTD", width=40)
        self.treeview_pedidos.column("Endereço", width=250)

        self.treeview_pedidos.pack(side="left", fill="both", expand=True)

        # Configurar a Scrollbar para a Treeview
        self.scrollbar_vertical.configure(command=self.treeview_pedidos.yview)

        # Exibir pedidos na Treeview
        self.exibir_pedidos()

        # Configurar o layout do frame_treeview
        frame_treeview.grid_rowconfigure(0, weight=1)
        frame_treeview.grid_columnconfigure(0, weight=1)

        # Remover espaçamento adicional
        self.frame_exibir_pedidos.grid_rowconfigure(2, weight=1)
        self.frame_exibir_pedidos.grid_columnconfigure(0, weight=1)
        self.frame_exibir_pedidos.grid_columnconfigure(1, weight=0)

    def exibir_pedidos(self):
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT pedidos.id_pedido, clientes.nome_cliente, pedidos.data_pedido, pedidos.descricao, pedidos.quantidade, pedidos.endereco
        FROM pedidos
        JOIN clientes ON pedidos.id_cliente = clientes.id_cliente
        ''')

        rows = cursor.fetchall()
        self.treeview_pedidos.delete(*self.treeview_pedidos.get_children())

        for row in rows:
            self.treeview_pedidos.insert("", "end", values=row)

        conn.close()

    def adicionar_cliente(self):
        nome_cliente = self.entry_nome_cliente.get()
        if not nome_cliente:
            messagebox.showwarning("Atenção", "O nome do cliente não pode estar vazio.")
            return

        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        # Normalizar o nome do cliente para evitar duplicação insensível a maiúsculas/minúsculas
        nome_cliente_normalizado = nome_cliente.strip().lower()

        # Verificar se o cliente já está cadastrado
        cursor.execute('''SELECT id_cliente FROM clientes WHERE LOWER(nome_cliente) = ?''', (nome_cliente_normalizado,))
        cliente_existente = cursor.fetchone()

        if cliente_existente:
            messagebox.showwarning("Aviso", "Cliente já cadastrado.")
        else:
            # Adicionar o cliente ao banco de dados
            cursor.execute('''INSERT INTO clientes (nome_cliente) VALUES (?)''', (nome_cliente,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso!")

        conn.close()
        self.entry_nome_cliente.delete(0, tk.END)

    def adicionar_pedido(self):
        cliente = self.entry_cliente.get()
        data_pedido = self.entry_data_pedido.get()
        descricao = self.entry_descricao.get()
        quantidade = self.entry_quantidade.get()
        cep = self.entry_endereco.get()

        if not cliente or not data_pedido or not descricao or not quantidade or not cep:
            messagebox.showwarning("Atenção", "Todos os campos devem ser preenchidos.")
            return

        endereco_completo = self.buscar_endereco_cep(cep)

        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id_cliente FROM clientes WHERE LOWER(nome_cliente) = LOWER(?)
        ''', (cliente,))
        cliente_id = cursor.fetchone()

        if cliente_id:
            cliente_id = cliente_id[0]
        else:
            messagebox.showwarning("Atenção", "Cliente não encontrado.")
            return

        cursor.execute('''
        INSERT INTO pedidos (id_cliente, data_pedido, descricao, quantidade, endereco)
        VALUES (?, ?, ?, ?, ?)
        ''', (cliente_id, data_pedido, descricao, quantidade, endereco_completo))

        conn.commit()
        conn.close()

        self.entry_cliente.delete(0, tk.END)
        self.entry_data_pedido.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_endereco.delete(0, tk.END)

        messagebox.showinfo("Sucesso", "Pedido adicionado com sucesso!")
        self.exibir_pedidos()

    #FUNÇÃO Q CHAMA A API DE CEP DOS CORREIOS
    def buscar_endereco_cep(self, cep):
        try:
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            data = response.json()

            if "erro" in data:
                messagebox.showerror("Erro", "CEP não encontrado.")
                return ""

            # Montar o endereço completo
            endereco = f"{data['logradouro']}, {data['bairro']}, {data['localidade']} - {data['uf']}"
            return endereco

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar CEP: {e}")
            return ""

    #ATUALIZA A TABELA CONFORME OQ É DIGITADO NA BARRA DE PESQUISA
    def atualizar_pesquisa(self, event=None):
        pesquisa = self.entry_pesquisa_principal.get()
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT pedidos.id_pedido, clientes.nome_cliente, pedidos.data_pedido, pedidos.descricao, pedidos.quantidade, pedidos.endereco
        FROM pedidos
        JOIN clientes ON pedidos.id_cliente = clientes.id_cliente
        WHERE clientes.nome_cliente LIKE ? OR pedidos.data_pedido LIKE ? OR pedidos.descricao LIKE ? OR pedidos.endereco LIKE ?
        ''', (f'%{pesquisa}%', f'%{pesquisa}%', f'%{pesquisa}%', f'%{pesquisa}%'))

        rows = cursor.fetchall()
        self.treeview_pedidos.delete(*self.treeview_pedidos.get_children())

        for row in rows:
            self.treeview_pedidos.insert("", "end", values=row)

        conn.close()

    #ATUALIZA A TABELA CONFORME OQ É DIGITADO NA BARRA DE PESQUISA POR I.D
    def atualizar_pesquisa_id(self, event=None):
        pesquisa_id = self.entry_pesquisa_id.get()
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT pedidos.id_pedido, clientes.nome_cliente, pedidos.data_pedido, pedidos.descricao, pedidos.quantidade, pedidos.endereco
        FROM pedidos
        JOIN clientes ON pedidos.id_cliente = clientes.id_cliente
        WHERE pedidos.id_pedido LIKE ?
        ''', (f'%{pesquisa_id}%',))

        rows = cursor.fetchall()
        self.treeview_pedidos.delete(*self.treeview_pedidos.get_children())

        for row in rows:
            self.treeview_pedidos.insert("", "end", values=row)

        conn.close()

    #função para o o botão "ver clientes cadastrados". Cria a janela que mostra os clientes já cadastrados
    def ver_clientes_cadastrados(self):

        # Função para excluir cliente
        def excluir_cliente():
            # Verificar se algum cliente foi selecionado
            if treeview_clientes.selection():
                # Fazer com que a janela principal seja o topo
                self.root.attributes("-topmost", True)
                self.root.lift()
                self.root.focus_force()

            # Exibir messagebox para confirmação de exclusão
                resposta = messagebox.askquestion("Confirmação", 
                                                  "Tem certeza que deseja excluir esse cliente? Essa ação é irreversível.", 
                                                  icon='warning')
            # Restaurar o comportamento padrão da janela principal
            self.root.attributes("-topmost", False)

            if resposta == 'yes':
                item = treeview_clientes.selection()[0]
                id_cliente = treeview_clientes.item(item, "values")[0]

                # Remover cliente do banco de dados
                conn = sqlite3.connect('sistema_pedidos.db')
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM clientes
                    WHERE id_cliente = ?
                ''', (id_cliente,))
                conn.commit()
                conn.close()

                # Remover cliente da Treeview
                treeview_clientes.delete(item)

        # Criar nova janela
        janela_clientes = ctk.CTkToplevel(self.root)
        janela_clientes.title("Clientes Cadastrados")
        janela_clientes.geometry("600x400")

        # Garantir que a janela seja sempre exibida no topo
        janela_clientes.attributes("-topmost", True)

        # Frame para a Treeview
        frame_treeview = ctk.CTkFrame(janela_clientes)
        frame_treeview.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar_vertical = ctk.CTkScrollbar(frame_treeview, orientation="vertical")
        scrollbar_vertical.pack(side="right", fill="y")

        # Criação da Treeview para exibir clientes e último pedido
        treeview_clientes = ttk.Treeview(
        frame_treeview,
        columns=("ID", "Cliente", "Último Pedido"),
        show='headings',
        yscrollcommand=scrollbar_vertical.set
        )

        # Configurar cabeçalhos das colunas
        treeview_clientes.heading("ID", text="ID")
        treeview_clientes.heading("Cliente", text="Cliente")
        treeview_clientes.heading("Último Pedido", text="Último Pedido")

        # Configurar larguras das colunas
        treeview_clientes.column("ID", width=50)
        treeview_clientes.column("Cliente", width=200)
        treeview_clientes.column("Último Pedido", width=150)

        treeview_clientes.pack(side="left", fill="both", expand=True)

        # Configurar a Scrollbar para a Treeview
        scrollbar_vertical.configure(command=treeview_clientes.yview)

        # Frame abaixo da Treeview para a barra de pesquisa e botões
        frame_opcoes = ctk.CTkFrame(janela_clientes)
        frame_opcoes.pack(fill="x", padx=10, pady=(0, 10))

        # Barra de pesquisa
        entry_pesquisa = ctk.CTkEntry(frame_opcoes, placeholder_text="Pesquise por cliente...")
        entry_pesquisa.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Botão de Editar Cliente
        botao_editar = ctk.CTkButton(frame_opcoes, text="Editar Cliente", command=lambda: editar_cliente())
        botao_editar.pack(side="left", padx=(0, 10))

        # Botão de Excluir Cliente
        botao_excluir = ctk.CTkButton(frame_opcoes, text="Excluir Cliente", command=excluir_cliente)
        botao_excluir.pack(side="left")

        # Conectar ao banco de dados e buscar dados
        conn = sqlite3.connect('sistema_pedidos.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT clientes.id_cliente, clientes.nome_cliente, MAX(pedidos.data_pedido)
        FROM clientes
        LEFT JOIN pedidos ON clientes.id_cliente = pedidos.id_cliente
        GROUP BY clientes.id_cliente
        ''')

        rows = cursor.fetchall()

        # Inserir dados na Treeview
        for row in rows:
            treeview_clientes.insert("", "end", values=row)

        conn.close()

        # Função para filtrar a Treeview com base na BARRA DE pesquisa
        def filtrar_treeview():
            query = entry_pesquisa.get().lower()
            for item in treeview_clientes.get_children():
                treeview_clientes.delete(item)

            for row in rows:
                if query in str(row[0]).lower() or query in row[1].lower():
                    treeview_clientes.insert("", "end", values=row)

        # Associar o evento de digitação à função de filtragem
        entry_pesquisa.bind("<KeyRelease>", lambda event: filtrar_treeview())

        # Função para editar o nome do cliente
        def editar_cliente():
            selected_item = treeview_clientes.selection()
            if selected_item:
                item = selected_item[0]
                old_name = treeview_clientes.item(item, "values")[1]

                # Obter a posição da célula para colocar o Entry
                x, y, width, height = treeview_clientes.bbox(item, column="Cliente")

            # Criar um Entry sobre a célula selecionada
            entry_edit = ctk.CTkEntry(frame_treeview, width=width)
            entry_edit.place(x=x, y=y, anchor="nw")
            entry_edit.insert(0, old_name)
            entry_edit.focus()

            # Função para salvar a edição
            def salvar_edicao(event):
                novo_nome = entry_edit.get()
                id_cliente = treeview_clientes.item(item, "values")[0]

                # Atualizar na Treeview
                treeview_clientes.item(item, values=(id_cliente, novo_nome, treeview_clientes.item(item, "values")[2]))

                # Atualizar no banco de dados
                conn = sqlite3.connect('sistema_pedidos.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE clientes
                    SET nome_cliente = ?
                    WHERE id_cliente = ?
                ''', (novo_nome, id_cliente))
                conn.commit()
                conn.close()

                # Remover o Entry após salvar
                entry_edit.destroy()

            entry_edit.bind("<Return>", salvar_edicao)

    #FUNÇÃO PARA EDITAR OS PEDIDOS NA PRÓPRIA TABELA
    def atualizar_endereco(self, event=None):
        novo_cep = self.entry_edit_endereco.get()
        endereco_completo = self.buscar_endereco_cep(novo_cep)
        self.entry_edit_endereco.delete(0, 'end')
        self.entry_edit_endereco.insert(0, endereco_completo)

    def limpar_edicao(self):
        # Verifica se os widgets de edição existem antes de tentar destruí-los
        if self.entry_edit_cliente:
            self.entry_edit_cliente.destroy()
        if self.entry_edit_data:
            self.entry_edit_data.destroy()
        if self.entry_edit_descricao:
            self.entry_edit_descricao.destroy()
        if self.entry_edit_quantidade:
            self.entry_edit_quantidade.destroy()
        if self.entry_edit_endereco:
            self.entry_edit_endereco.destroy()

        # Limpa os atributos para evitar referências antigas
        self.entry_edit_cliente = None
        self.entry_edit_data = None
        self.entry_edit_descricao = None
        self.entry_edit_quantidade = None
        self.entry_edit_endereco = None

    def ativar_edicao_pedido(self):
        selected_item = self.treeview_pedidos.selection()
        
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado. Por favor, selecione um pedido para editar.")
            return
        
        # Limpar a edição anterior, se existir
        self.limpar_edicao()

        item = selected_item[0]
        values = self.treeview_pedidos.item(item, "values")

        # Obter valores da linha selecionada
        old_cliente = values[1] if len(values) > 1 else ""
        old_data = values[2] if len(values) > 2 else ""
        old_descricao = values[3] if len(values) > 3 else ""
        old_quantidade = values[4] if len(values) > 4 else ""
        old_endereco = values[5] if len(values) > 5 else ""

        # Obter a posição da célula para colocar os Entries
        try:
            x_cliente, y_cliente, width_cliente, height_cliente = self.treeview_pedidos.bbox(item, column="Cliente")
            x_data, y_data, width_data, height_data = self.treeview_pedidos.bbox(item, column="Data")
            x_descricao, y_descricao, width_descricao, height_descricao = self.treeview_pedidos.bbox(item, column="Descrição")
            x_quantidade, y_quantidade, width_quantidade, height_quantidade = self.treeview_pedidos.bbox(item, column="QTD")
            x_endereco, y_endereco, width_endereco, height_endereco = self.treeview_pedidos.bbox(item, column="Endereço")
        except TclError as e:
            print(f"Erro ao obter posição da célula: {e}")
            return

        # Criar os Entries para editar os valores
        self.entry_edit_cliente = ctk.CTkEntry(self.frame_exibir_pedidos, width=width_cliente)
        self.entry_edit_cliente.place(x=x_cliente, y=y_cliente, anchor="nw")
        self.entry_edit_cliente.insert(0, old_cliente)
        self.entry_edit_cliente.focus()

        self.entry_edit_data = ctk.CTkEntry(self.frame_exibir_pedidos, width=width_data)
        self.entry_edit_data.place(x=x_data, y=y_data, anchor="nw")
        self.entry_edit_data.insert(0, old_data)

        self.entry_edit_descricao = ctk.CTkEntry(self.frame_exibir_pedidos, width=width_descricao)
        self.entry_edit_descricao.place(x=x_descricao, y=y_descricao, anchor="nw")
        self.entry_edit_descricao.insert(0, old_descricao)

        self.entry_edit_quantidade = ctk.CTkEntry(self.frame_exibir_pedidos, width=width_quantidade)
        self.entry_edit_quantidade.place(x=x_quantidade, y=y_quantidade, anchor="nw")
        self.entry_edit_quantidade.insert(0, old_quantidade)

        self.entry_edit_endereco = ctk.CTkEntry(self.frame_exibir_pedidos, width=width_endereco)
        self.entry_edit_endereco.place(x=x_endereco, y=y_endereco, anchor="nw")
        self.entry_edit_endereco.insert(0, old_endereco)

        # Atualizar o endereço quando o Enter é pressionado
        self.entry_edit_endereco.bind("<Return>", self.atualizar_endereco)

        # Função para salvar a edição
        def salvar_edicao_pedidos(event):
            try:
                novo_cliente = self.entry_edit_cliente.get()
                nova_data = self.entry_edit_data.get()
                nova_descricao = self.entry_edit_descricao.get()
                nova_quantidade = int(self.entry_edit_quantidade.get())
                novo_endereco = self.entry_edit_endereco.get()
                id_pedido = values[0]

                # Verificar se o novo cliente existe
                conn = sqlite3.connect('sistema_pedidos.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id_cliente FROM clientes WHERE nome_cliente = ?', (novo_cliente,))
                cliente_id = cursor.fetchone()
                conn.close()

                if cliente_id:
                    cliente_id = cliente_id[0]
                    # Atualizar na Treeview
                    self.treeview_pedidos.item(item, values=(id_pedido, novo_cliente, nova_data, nova_descricao, nova_quantidade, novo_endereco))

                    # Atualizar no banco de dados
                    conn = sqlite3.connect('sistema_pedidos.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE pedidos
                        SET id_cliente = ?, data_pedido = ?, descricao = ?, quantidade = ?, endereco = ?
                        WHERE id_pedido = ?
                    ''', (cliente_id, nova_data, nova_descricao, nova_quantidade, novo_endereco, id_pedido))
                    conn.commit()
                    conn.close()

                    # Remover os Entries após salvar
                    self.limpar_edicao()

                    # Mostrar mensagem de sucesso
                    messagebox.showinfo("Sucesso", "Alterações Salvas!")
                else:
                    messagebox.showwarning("Atenção", "Cliente não encontrado.")
            except ValueError:
                messagebox.showwarning("Atenção", "Quantidade deve ser um número válido.")

        self.entry_edit_cliente.bind("<Return>", salvar_edicao_pedidos)
        self.entry_edit_data.bind("<Return>", salvar_edicao_pedidos)
        self.entry_edit_descricao.bind("<Return>", salvar_edicao_pedidos)
        self.entry_edit_quantidade.bind("<Return>", salvar_edicao_pedidos)
        self.entry_edit_endereco.bind("<Return>", salvar_edicao_pedidos)

    #FUNÇÃO PARA EXCLUIR PEDIDOS NA TABELA
    def excluir_pedido(self):
        selected_item = self.treeview_pedidos.selection()

        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado. Por favor, selecione um pedido para excluir.")
            return  # Este return deve estar indentado dentro do if

        resposta = messagebox.askquestion("Confirmação", 
                                          "Tem certeza que deseja excluir este pedido?", 
                                          icon='warning')
        if resposta == 'yes':
            item_id = self.treeview_pedidos.item(selected_item, "values")[0]

            conn = sqlite3.connect('sistema_pedidos.db')
            cursor = conn.cursor()

            cursor.execute('''
            DELETE FROM pedidos
            WHERE id_pedido = ?
            ''', (item_id,))

            conn.commit()
            conn.close()

            # Remover da Treeview
            self.treeview_pedidos.delete(selected_item)
            messagebox.showinfo("Sucesso", "Pedido excluído com sucesso!")

#INICIA O PROGRAMA
if __name__ == "__main__":
    root = ctk.CTk()
    app = SistemaPedidosApp(root)
    root.mainloop()
