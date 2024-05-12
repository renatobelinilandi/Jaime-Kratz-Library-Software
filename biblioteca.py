import tkinter as tk
from tkinter import simpledialog, messagebox, Frame, Button, Label, Listbox, Toplevel
from datetime import datetime, timedelta
import json
import os
import unicodedata

# Cores e estilos
background_color = '#f0f0f0'
text_color = '#333'
accent_color = '#FFB347'  # Laranja pastel
button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color}
label_style = {'font': ('JetBrains Mono', 14, 'bold'), 'background': background_color, 'foreground': text_color}


def contar_alugueis_consecutivos(livro, nome_locatario):
    count = 0
    for emprestimo in livro['emprestimos']:
        if emprestimo['nome_locatario'] == nome_locatario:
            count += 1
        else:
            break
    return count


class Biblioteca:
    def __init__(self):
        self.dados_arquivo = 'library_data.json'
        self.livros = self.carregar_dados()
        self.alugueis_consecutivos = {}

    def carregar_dados(self):
        if os.path.exists(self.dados_arquivo):
            if os.path.getsize(self.dados_arquivo) > 0:  # Verifica se o arquivo não está vazio
                with open(self.dados_arquivo, 'r') as arquivo:
                    return json.load(arquivo)
            else:
                return []  # Retorna uma lista vazia se o arquivo estiver vazio
        else:
            # Se o arquivo não existir, cria um arquivo vazio com uma lista vazia
            with open(self.dados_arquivo, 'w') as arquivo:
                json.dump([], arquivo, indent=4)
            return []

    def salvar_dados(self):
        with open(self.dados_arquivo, 'w') as arquivo:
            json.dump(self.livros, arquivo, indent=4)

    def adicionar_livro(self, titulo, autor, quantidade):
        # Verifica se o livro já existe
        for livro in self.livros:
            if self.remover_acentos(livro['titulo']).lower() == self.remover_acentos(
                    titulo).lower() and self.remover_acentos(livro['autor']).lower() == self.remover_acentos(
                    autor).lower():
                livro['quantidade'] += quantidade
                self.salvar_dados()
                return "Quantidade atualizada para livro existente."
        # Se não existe, adiciona novo
        self.livros.append({'titulo': titulo, 'autor': autor, 'quantidade': quantidade, 'emprestimos': []})
        self.salvar_dados()
        return "Livro novo adicionado."

    def adicionar_unidades(self, titulo, unidades):
        for livro in self.livros:
            if self.remover_acentos(livro['titulo']).lower() == self.remover_acentos(titulo).lower():
                livro['quantidade'] += unidades
                self.salvar_dados()
                return f"Adicionadas {unidades} unidades ao livro '{titulo}'."
        return "Livro não encontrado."

    def remover_livro(self, titulo, autor):
        for livro in self.livros:
            if self.remover_acentos(livro['titulo']).lower() == self.remover_acentos(titulo).lower() and \
                    self.remover_acentos(livro['autor']).lower() == self.remover_acentos(autor).lower():
                if livro['quantidade'] > 0:
                    livro['quantidade'] -= 1
                    self.salvar_dados()
                    return "Livro removido com sucesso."
                return "Todas as cópias já foram removidas."
        return "Livro não encontrado."

    def remover_livro_completo(self, titulo):
        self.livros = [livro for livro in self.livros if
                       self.remover_acentos(livro['titulo']).lower() != self.remover_acentos(titulo).lower()]
        self.salvar_dados()
        return "Livro removido completamente."

    def remover_unidades(self, titulo, unidades):
        for livro in self.livros:
            if self.remover_acentos(livro['titulo']).lower() == self.remover_acentos(titulo).lower():
                if livro['quantidade'] >= unidades:
                    livro['quantidade'] -= unidades
                    self.salvar_dados()
                    return f"Removidas {unidades} unidades do livro '{titulo}'."
        return "Quantidade insuficiente para remoção ou livro não encontrado."

    def buscar_livro(self, titulo):
        titulo = self.remover_acentos(titulo).lower()
        return [livro for livro in self.livros if titulo in self.remover_acentos(livro['titulo']).lower()]

    def alugar_livro(self, titulo, autor, nome_locatario, numero_sala):
        nome_locatario = nome_locatario.upper()
        numero_sala = numero_sala.upper()
        for livro in self.livros:
            if self.remover_acentos(livro['titulo']).lower() == self.remover_acentos(titulo).lower() and \
                    self.remover_acentos(livro['autor']).lower() == self.remover_acentos(autor).lower():
                if livro['quantidade'] > 0:
                    livro['quantidade'] -= 1
                    emprestimo = {
                        'nome_locatario': nome_locatario,
                        'numero_sala': numero_sala,
                        'data_devolucao': (datetime.now() + timedelta(days=14)).strftime('%d/%m/%Y'),
                        'devolvido': False
                    }
                    livro['emprestimos'].append(emprestimo)
                    self.salvar_dados()
                    # Incrementar o contador de aluguéis consecutivos
                    self.alugueis_consecutivos[nome_locatario] = self.alugueis_consecutivos.get(nome_locatario, 0) + 1
                    return "Livro alugado com sucesso."
                return "Todos os exemplares estão alugados."
        return "Livro não encontrado."

    def devolver_livro(self, nome_locatario):
        nome_locatario = nome_locatario.upper()  # Assegurando que o nome está em maiúsculas
        emprestimo_removido = False
        for livro in self.livros:
            emprestimos_atualizados = []
            for emprestimo in livro['emprestimos']:
                if emprestimo['nome_locatario'] == nome_locatario and not emprestimo['devolvido']:
                    emprestimo_removido = True
                    livro['quantidade'] += 1  # Devolve o livro ao estoque
                else:
                    emprestimos_atualizados.append(emprestimo)
            livro['emprestimos'] = emprestimos_atualizados
        if emprestimo_removido:
            self.salvar_dados()
            return "Empréstimo devolvido e removido com sucesso."
        return "Nenhum empréstimo ativo encontrado para este locatário."

    def buscar_livros_atrasados(self):
        hoje = datetime.now().date()
        atrasados = []
        for livro in self.livros:
            for emprestimo in livro['emprestimos']:
                if (datetime.strptime(emprestimo['data_devolucao'], '%d/%m/%Y').date() < hoje and not
                emprestimo.get('devolvido', False)):
                    emprestimo_info = {
                        'titulo': livro['titulo'],
                        'autor': livro['autor'],
                        'nome_locatario': emprestimo['nome_locatario'],
                        'numero_sala': emprestimo['numero_sala'],
                        'data_devolucao': emprestimo['data_devolucao'],
                        'alugueis_consecutivos': contar_alugueis_consecutivos(livro, emprestimo['nome_locatario'])
                    }
                    atrasados.append(emprestimo_info)
        return atrasados

    def buscar_emprestimos_ativos(self):
        active_loans = []
        for livro in self.livros:
            for emprestimo in livro['emprestimos']:
                if not emprestimo.get('devolvido', False):
                    emprestimo_info = {
                        'titulo': livro['titulo'],
                        'autor': livro['autor'],
                        'nome_locatario': emprestimo['nome_locatario'],
                        'numero_sala': emprestimo['numero_sala'],
                        'data_devolucao': emprestimo['data_devolucao'],
                        'alugueis_consecutivos': contar_alugueis_consecutivos(livro, emprestimo['nome_locatario'])
                    }
                    active_loans.append(emprestimo_info)
        return active_loans

    def buscar_alugueis_ativos_por_nome_ou_titulo(self, pesquisa):
        pesquisa = self.remover_acentos(pesquisa).lower()  # Normaliza a pesquisa para minúsculas
        ativos = self.buscar_emprestimos_ativos()  # Pega todos os empréstimos ativos
        # Filtra os empréstimos que contêm a pesquisa no nome do locatário, título do livro ou número da sala
        resultado = [emprestimo for emprestimo in ativos if
                     pesquisa in self.remover_acentos(emprestimo['nome_locatario']).lower() or
                     pesquisa in self.remover_acentos(emprestimo['titulo']).lower() or
                     pesquisa in self.remover_acentos(emprestimo['numero_sala']).lower()]
        return resultado

    @staticmethod
    def remover_acentos(texto):
        return ''.join(ch for ch in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(ch))


class LibraryGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Gerenciamento de Biblioteca")
        self.master.geometry("800x600")
        self.master.resizable(False, False)
        self.centralizar_janela()
        self.library = Biblioteca()
        self.frame = None
        self.alternar_frame(TelasPrincipais)

    def centralizar_janela(self):
        largura_tela = self.master.winfo_screenwidth()
        altura_tela = self.master.winfo_screenheight()
        x = int((largura_tela / 2) - (800 / 2))
        y = int((altura_tela / 2) - (600 / 2))
        self.master.geometry(f'800x600+{x}+{y}')

    def alternar_frame(self, classe_frame):
        novo_frame = classe_frame(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = novo_frame
        self.frame.pack()


class TelasPrincipais(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Biblioteca Jaime Kratz", **label_style).pack(pady=20)
        Button(self, text="Área do locatário", command=lambda: gui.alternar_frame(FuncoesUsuario), height=3, width=25,
               **button_style).pack(pady=20)
        Button(self, text="Painel de Administração", command=lambda: admin_login(gui), height=3, width=25,
               **button_style).pack(pady=20)


class PainelAdmin(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Painel de Administração", **label_style).pack(pady=20)
        Button(self, text="Adicionar Livro", command=lambda: add_book(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Remover Livro", command=lambda: remove_book(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Buscar Empréstimos Ativos", command=lambda: search_active_loans(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Ver Livros em Atraso", command=lambda: view_overdue_books(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Voltar ao Principal", command=lambda: gui.alternar_frame(TelasPrincipais), height=3,
               width=25,
               **button_style).pack(pady=20)


class FuncoesUsuario(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Área do Locatário", **label_style).pack(pady=20)
        Button(self, text="Buscar Livros", command=lambda: search_books(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Alugar Livro", command=lambda: show_book_selection(gui), height=3,
               width=25,
               **button_style).pack(pady=10)
        Button(self, text="Devolver Livro", command=lambda: return_book(gui), height=3, width=25,
               **button_style).pack(pady=10)
        Button(self, text="Voltar ao Principal", command=lambda: gui.alternar_frame(TelasPrincipais), height=3,
               width=25,
               **button_style).pack(pady=20)


def admin_login(gui):
    senha = simpledialog.askstring("Login de Admin", "Digite a senha:", show='*')
    if senha == "123":
        gui.alternar_frame(PainelAdmin)
    else:
        messagebox.showerror("Erro", "Senha incorreta.")


def add_book(gui):
    resposta = messagebox.askyesno("Adicionar Livro", "Deseja adicionar um livro novo?")
    if resposta:
        # Adicionar um novo livro
        titulo = simpledialog.askstring("Adicionar Livro Novo", "Digite o título do livro:")
        autor = simpledialog.askstring("Adicionar Livro Novo", "Digite o nome do autor:")
        quantidade = simpledialog.askinteger("Adicionar Livro Novo", "Digite a quantidade de unidades:",
                                             minvalue=1)
        if titulo and autor and quantidade:
            if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar o livro"
                                                          f" '{titulo}' com {quantidade} unidades. Tem certeza?"):
                resultado = gui.library.adicionar_livro(titulo, autor, quantidade)
                messagebox.showinfo("Adição de Livro", resultado)
    else:
        # Adicionar unidades a um livro existente
        titulo = simpledialog.askstring("Adicionar Unidades", "Digite o título do livro para adicionar"
                                                              " unidades:")
        if titulo:
            livro_encontrado = gui.library.buscar_livro(titulo)
            if livro_encontrado:
                unidades = simpledialog.askinteger("Adicionar Unidades",
                                                   "Quantas unidades você deseja adicionar?",
                                                   minvalue=1)
                if unidades:
                    if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar"
                                                                  f" {unidades} unidades ao livro '{titulo}'"
                                                                  f". Tem certeza?"):
                        resultado = gui.library.adicionar_unidades(titulo, unidades)
                        messagebox.showinfo("Adição de Unidades", resultado)
            else:
                messagebox.showinfo("Erro", "Livro não encontrado.")
        else:
            messagebox.showinfo("Adicionar Unidades", "Você não digitou o título do livro.")


def remove_book(gui):
    titulo = simpledialog.askstring("Remover Livro", "Digite o título do livro que deseja remover:")
    if titulo:
        livros_encontrados = gui.library.buscar_livro(titulo)
        if livros_encontrados:
            livro = livros_encontrados[0]  # Assumindo que a busca retorna uma lista e pegando o primeiro resultado
            resposta = messagebox.askyesno("Remover Livro", "Deseja remover o livro completamente?")
            if resposta:
                if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover o livro"
                                                               f" '{livro['titulo']}' completamente. Tem certeza?"):
                    resultado = gui.library.remover_livro_completo(livro['titulo'])
                    messagebox.showinfo("Remoção de Livro", resultado)
            else:
                unidades = simpledialog.askinteger("Remover Unidades", "Quantas unidades do livro você"
                                                                       " deseja remover?", minvalue=1,
                                                   maxvalue=livro['quantidade'])
                if unidades:
                    if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover"
                                                                   f" {unidades} unidades do livro '{livro['titulo']}'"
                                                                   f". Tem certeza?"):
                        resultado = gui.library.remover_unidades(livro['titulo'], unidades)
                        messagebox.showinfo("Remoção de Unidades", resultado)
        else:
            messagebox.showinfo("Erro", "Livro não encontrado.")
    else:
        messagebox.showinfo("Remover Livro", "Você não digitou o nome do livro.")


def view_overdue_books(gui):
    livros_atrasados = gui.library.buscar_livros_atrasados()
    if livros_atrasados:
        info_livros = '\n'.join([f"\nTítulo: {livro['titulo']} - Escrito por: {livro['autor']}\nAlugado por:"
                                 f" {livro['nome_locatario']} na sala/função: {livro['numero_sala']}\nDevolução em:"
                                 f" {livro['data_devolucao']}\nAluguéis consecutivos: {livro['alugueis_consecutivos']}"
                                 f"\n{'-' * 40}" for livro in livros_atrasados])
        messagebox.showinfo("Livros em Atraso", info_livros)
    else:
        messagebox.showinfo("Livros em Atraso", "Nenhum livro em atraso encontrado.")


def search_active_loans(gui):
    pesquisa = simpledialog.askstring("Buscar Empréstimos Ativos",
                                      "Digite o nome, parte do título do livro, ou número da sala/função:")
    if pesquisa:
        emprestimos_ativos = gui.library.buscar_alugueis_ativos_por_nome_ou_titulo(pesquisa)
        if emprestimos_ativos:
            info_emprestimos = '\n'.join([f"Título: {emprestimo['titulo']} - Escrito por: {emprestimo['autor']}"
                                          f"\nAlugado por: {emprestimo['nome_locatario']} na sala/função:"
                                          f" {emprestimo['numero_sala']}\nDevolução em: {emprestimo['data_devolucao']}"
                                          f"\nAluguéis consecutivos: {emprestimo['alugueis_consecutivos']}\n{'-' * 40}"
                                          for emprestimo in emprestimos_ativos])
            messagebox.showinfo("Empréstimos Ativos", info_emprestimos)
        else:
            messagebox.showinfo("Empréstimos Ativos", "Nenhum empréstimo correspondente encontrado.")
    else:
        messagebox.showinfo("Buscar Empréstimos Ativos", "Você não digitou uma pesquisa.")



def search_books(gui):
    titulo_pesquisa = simpledialog.askstring("Buscar Livros", "Digite o título do livro ou parte dele:")
    if titulo_pesquisa:
        resultados = gui.library.buscar_livro(titulo_pesquisa)
        if resultados:
            livros = '\n'.join([f"\nTítulo: {livro['titulo']} - Escrito por: {livro['autor']} - Quantidade: {livro['quantidade']}\n{'-' * 40}" for livro in resultados])
            messagebox.showinfo("Resultados da Busca", livros)
        else:
            messagebox.showinfo("Resultados da Busca", "Nenhum livro encontrado.")
    else:
        messagebox.showinfo("Buscar Livros", "Você não digitou o título do livro.")



def show_book_selection(gui):
    titulo_pesquisa = simpledialog.askstring("Buscar Livros", "Digite o título do livro ou parte dele:")
    if titulo_pesquisa:
        resultados = gui.library.buscar_livro(titulo_pesquisa)
        if resultados:
            janela_selecao = Toplevel(gui.master)
            janela_selecao.title("Selecione um Livro para Alugar")
            largura_janela = 300
            altura_janela = 200
            largura_tela = janela_selecao.winfo_screenwidth()
            altura_tela = janela_selecao.winfo_screenheight()
            x = int((largura_tela / 2) - (largura_janela / 2))
            y = int((altura_tela / 2) - (altura_janela / 2))
            janela_selecao.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")
            janela_selecao.resizable(False, False)
            janela_selecao.grab_set()

            listbox = Listbox(janela_selecao, height=6, width=50, border=0)
            listbox.pack(padx=10, pady=10, fill="both", expand=True)

            for livro in resultados:
                listbox.insert(tk.END, f"{livro['titulo']} - {livro['autor']} - Quantidade:"
                                       f" {livro['quantidade']}")

            def selecionar_livro():
                livro_selecionado = listbox.curselection()
                if livro_selecionado:
                    livro_selecionado = resultados[livro_selecionado[0]]
                    nome_locatario = simpledialog.askstring("Alugar Livro", "Digite o seu nome:")
                    numero_sala = simpledialog.askstring("Alugar Livro", "Digite o número da sua sala"
                                                                         " ou função:")
                    if nome_locatario and numero_sala:
                        resultado = gui.library.alugar_livro(livro_selecionado['titulo'], livro_selecionado['autor'],
                                                             nome_locatario, numero_sala.upper())
                        messagebox.showinfo("Resultado", resultado)
                        janela_selecao.destroy()
                        gui.alternar_frame(FuncoesUsuario)

            Button(janela_selecao, text="Selecionar Livro", command=selecionar_livro).pack(pady=10)
        else:
            messagebox.showinfo("Buscar Livros", "Nenhum livro encontrado.")
    else:
        messagebox.showinfo("Buscar Livros", "Você não digitou o título do livro.")


def return_book(gui):
    nome_locatario = simpledialog.askstring("Devolver Livro", "Digite o seu nome:")
    if nome_locatario:
        resultado = gui.library.devolver_livro(nome_locatario)
        messagebox.showinfo("Resultado", resultado)


def executar_gui():
    raiz = tk.Tk()
    LibraryGUI(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    executar_gui()
