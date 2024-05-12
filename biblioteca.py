import tkinter as tk
from tkinter import simpledialog, messagebox, Frame, Button, Label, Listbox, Toplevel
from datetime import datetime, timedelta
import json
import os
import unicodedata

# Colors and styles
background_color = '#f0f0f0'
text_color = '#333'
accent_color = '#FFB347'  # Pastel orange
button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color}
label_style = {'font': ('JetBrains Mono', 14, 'bold'), 'background': background_color, 'foreground': text_color}


def count_consecutive_loans(book, tenant_name):
    count = 0
    for loan in book['loans']:
        if loan['tenant_name'] == tenant_name:
            count += 1
        else:
            break
    return count


class Library:
    def __init__(self):
        self.data_file = 'library_data.json'
        self.books = self.load_data()
        self.consecutive_loans = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            if os.path.getsize(self.data_file) > 0:  # Check if the file is not empty
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            else:
                return []  # Return an empty list if the file is empty
        else:
            # If the file does not exist, create an empty file with an empty list
            with open(self.data_file, 'w') as file:
                json.dump([], file, indent=4)
            return []

    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.books, file, indent=4)

    def add_book(self, title, author, quantity):
        # Check if the book already exists
        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(
                    title).lower() and self.remove_accents(book['author']).lower() == self.remove_accents(
                    author).lower():
                book['quantity'] += quantity
                self.save_data()
                return "Quantidade atualizada para livro existente."
        # If it does not exist, add new
        self.books.append({'title': title, 'author': author, 'quantity': quantity, 'loans': []})
        self.save_data()
        return "Livro novo adicionado."

    def add_units(self, title, units):
        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(title).lower():
                book['quantity'] += units
                self.save_data()
                return f"Adicionadas {units} unidades ao livro '{title}'."
        return "Livro não encontrado."

    def remove_book(self, title, author):
        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(title).lower() and \
                    self.remove_accents(book['author']).lower() == self.remove_accents(author).lower():
                if book['quantity'] > 0:
                    book['quantity'] -= 1
                    self.save_data()
                    return "Livro removido com sucesso."
                return "Todas as cópias já foram removidas."
        return "Livro não encontrado."

    def remove_complete_book(self, title):
        self.books = [book for book in self.books if
                      self.remove_accents(book['title']).lower() != self.remove_accents(title).lower()]
        self.save_data()
        return "Livro removido completamente."

    def remove_units(self, title, units):
        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(title).lower():
                if book['quantity'] >= units:
                    book['quantity'] -= units
                    self.save_data()
                    return f"Removidas {units} unidades do livro '{title}'."
        return "Quantidade insuficiente para remoção ou livro não encontrado."

    def find_book(self, title):
        title = self.remove_accents(title).lower()
        return [book for book in self.books if title in self.remove_accents(book['title']).lower()]

    def rent_book(self, title, author, tenant_name, room_number):
        tenant_name = tenant_name.upper()
        room_number = room_number.upper()
        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(title).lower() and \
                    self.remove_accents(book['author']).lower() == self.remove_accents(author).lower():
                if book['quantity'] > 0:
                    book['quantity'] -= 1
                    loan = {
                        'tenant_name': tenant_name,
                        'room_number': room_number,
                        'return_date': (datetime.now() + timedelta(days=14)).strftime('%d/%m/%Y'),
                        'returned': False
                    }
                    book['loans'].append(loan)
                    self.save_data()
                    # Increment the counter of consecutive rentals
                    self.consecutive_loans[tenant_name] = self.consecutive_loans.get(tenant_name, 0) + 1
                    return "Livro alugado com sucesso."
                return "Todos os exemplares estão alugados."
        return "Livro não encontrado."

    def return_book(self, tenant_name):
        tenant_name = tenant_name.upper()  # Ensuring the name is in uppercase
        loan_removed = False
        for book in self.books:
            updated_loans = []
            for loan in book['loans']:
                if loan['tenant_name'] == tenant_name and not loan['returned']:
                    loan_removed = True
                    book['quantity'] += 1  # Return the book to the stock
                else:
                    updated_loans.append(loan)
            book['loans'] = updated_loans
        if loan_removed:
            self.save_data()
            return "Empréstimo devolvido e removido com sucesso."
        return "Nenhum empréstimo ativo encontrado para este locatário."

    def find_overdue_books(self):
        today = datetime.now().date()
        overdue_books = []
        for book in self.books:
            for loan in book['loans']:
                if (datetime.strptime(loan['return_date'], '%d/%m/%Y').date() < today and not
                loan.get('returned', False)):
                    loan_info = {
                        'title': book['title'],
                        'author': book['author'],
                        'tenant_name': loan['tenant_name'],
                        'room_number': loan['room_number'],
                        'return_date': loan['return_date'],
                        'consecutive_loans': count_consecutive_loans(book, loan['tenant_name'])
                    }
                    overdue_books.append(loan_info)
        return overdue_books

    def find_active_loans(self):
        active_loans = []
        for book in self.books:
            for loan in book['loans']:
                if not loan.get('returned', False):
                    loan_info = {
                        'title': book['title'],
                        'author': book['author'],
                        'tenant_name': loan['tenant_name'],
                        'room_number': loan['room_number'],
                        'return_date': loan['return_date'],
                        'consecutive_loans': count_consecutive_loans(book, loan['tenant_name'])
                    }
                    active_loans.append(loan_info)
        return active_loans

    def find_active_loans_by_name_or_title(self, search_query):
        search_query = self.remove_accents(search_query).lower()  # Normalize the search to lowercase
        active_loans = self.find_active_loans()  # Get all active loans
        # Filter loans that contain the search in the tenant's name, book title, or room number
        result = [loan for loan in active_loans if
                 search_query in self.remove_accents(loan['tenant_name']).lower() or
                 search_query in self.remove_accents(loan['title']).lower() or
                 search_query in self.remove_accents(loan['room_number']).lower()]
        return result

    @staticmethod
    def remove_accents(text):
        return ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))


class LibraryGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Library Management System")
        self.master.geometry("800x600")
        self.master.resizable(False, False)
        self.center_window()
        self.library = Library()
        self.frame = None
        self.switch_frame(MainScreens)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = int((screen_width / 2) - (800 / 2))
        y = int((screen_height / 2) - (600 / 2))
        self.master.geometry(f'800x600+{x}+{y}')

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = new_frame
        self.frame.pack()


class MainScreens(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Biblioteca Jaime Kratz", **label_style).pack(pady=20)
        Button(self, text="Área do locatário", command=lambda: gui.switch_frame(TenantFunctions), height=3, width=25,
               **button_style).pack(pady=20)
        Button(self, text="Painel de Administração", command=lambda: admin_login(gui), height=3, width=25,
               **button_style).pack(pady=20)


class AdminPanel(Frame):
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
        Button(self, text="Voltar ao Principal", command=lambda: gui.switch_frame(MainScreens), height=3,
               width=25,
               **button_style).pack(pady=20)


class TenantFunctions(Frame):
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
        Button(self, text="Voltar ao Principal", command=lambda: gui.switch_frame(MainScreens), height=3,
               width=25,
               **button_style).pack(pady=20)


def admin_login(gui):
    password = simpledialog.askstring("Login de Admin", "Digite a senha:", show='*')
    if password == "123":
        gui.switch_frame(AdminPanel)
    else:
        messagebox.showerror("Erro", "Senha incorreta.")


def add_book(gui):
    response = messagebox.askyesno("Adicionar Livro", "Deseja adicionar um livro novo?")
    if response:
        # Add a new book
        title = simpledialog.askstring("Adicionar Livro Novo", "Digite o título do livro:")
        author = simpledialog.askstring("Adicionar Livro Novo", "Digite o nome do autor:")
        quantity = simpledialog.askinteger("Adicionar Livro Novo", "Digite a quantidade de unidades:",
                                           minvalue=1)
        if title and author and quantity:
            if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar o livro"
                                                          f" '{title}' com {quantity} unidades. Tem certeza?"):
                result = gui.library.add_book(title, author, quantity)
                messagebox.showinfo("Adição de Livro", result)
    else:
        # Add units to an existing book
        title = simpledialog.askstring("Adicionar Unidades", "Digite o título do livro para adicionar"
                                                              " unidades:")
        if title:
            book_found = gui.library.find_book(title)
            if book_found:
                units = simpledialog.askinteger("Adicionar Unidades",
                                                "Quantas unidades você deseja adicionar?",
                                                minvalue=1)
                if units:
                    if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar"
                                                                  f" {units} unidades ao livro '{title}'"
                                                                  f". Tem certeza?"):
                        result = gui.library.add_units(title, units)
                        messagebox.showinfo("Adição de Unidades", result)
            else:
                messagebox.showinfo("Erro", "Livro não encontrado.")
        else:
            messagebox.showinfo("Adicionar Unidades", "Você não digitou o título do livro.")


def remove_book(gui):
    title = simpledialog.askstring("Remover Livro", "Digite o título do livro que deseja remover:")
    if title:
        books_found = gui.library.find_book(title)
        if books_found:
            book = books_found[0]  # Assuming the search returns a list and taking the first result
            response = messagebox.askyesno("Remover Livro", "Deseja remover o livro completamente?")
            if response:
                if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover o livro"
                                                               f" '{book['title']}' completamente. Tem certeza?"):
                    result = gui.library.remove_complete_book(book['title'])
                    messagebox.showinfo("Remoção de Livro", result)
            else:
                units = simpledialog.askinteger("Remover Unidades", "Quantas unidades do livro você"
                                                                    " deseja remover?", minvalue=1,
                                                maxvalue=book['quantity'])
                if units:
                    if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover"
                                                                   f" {units} unidades do livro '{book['title']}'"
                                                                   f". Tem certeza?"):
                        result = gui.library.remove_units(book['title'], units)
                        messagebox.showinfo("Remoção de Unidades", result)
        else:
            messagebox.showinfo("Erro", "Livro não encontrado.")
    else:
        messagebox.showinfo("Remover Livro", "Você não digitou o nome do livro.")


def view_overdue_books(gui):
    overdue_books = gui.library.find_overdue_books()
    if overdue_books:
        book_info = '\n'.join([f"\nTítulo: {book['title']} - Escrito por: {book['author']}\nAlugado por:"
                               f" {book['tenant_name']} na sala/função: {book['room_number']}\nDevolução em:"
                               f" {book['return_date']}\nAluguéis consecutivos: {book['consecutive_loans']}"
                               f"\n{'-' * 40}" for book in overdue_books])
        messagebox.showinfo("Livros em Atraso", book_info)
    else:
        messagebox.showinfo("Livros em Atraso", "Nenhum livro em atraso encontrado.")


def search_active_loans(gui):
    search_query = simpledialog.askstring("Buscar Empréstimos Ativos",
                                          "Digite o nome, parte do título do livro, ou número da sala/função:")
    if search_query:
        active_loans = gui.library.find_active_loans_by_name_or_title(search_query)
        if active_loans:
            loan_info = '\n'.join([f"Título: {loan['title']} - Escrito por: {loan['author']}"
                                   f"\nAlugado por: {loan['tenant_name']} na sala/função:"
                                   f" {loan['room_number']}\nDevolução em: {loan['return_date']}"
                                   f"\nAluguéis consecutivos: {loan['consecutive_loans']}\n{'-' * 40}"
                                   for loan in active_loans])
            messagebox.showinfo("Empréstimos Ativos", loan_info)
        else:
            messagebox.showinfo("Empréstimos Ativos", "Nenhum empréstimo correspondente encontrado.")
    else:
        messagebox.showinfo("Buscar Empréstimos Ativos", "Você não digitou uma pesquisa.")


def search_books(gui):
    title_search = simpledialog.askstring("Buscar Livros", "Digite o título do livro ou parte dele:")
    if title_search:
        results = gui.library.find_book(title_search)
        if results:
            books = '\n'.join([f"\nTítulo: {book['title']} - Escrito por: {book['author']} - Quantidade: {book['quantity']}\n{'-' * 40}" for book in results])
            messagebox.showinfo("Resultados da Busca", books)
        else:
            messagebox.showinfo("Resultados da Busca", "Nenhum livro encontrado.")
    else:
        messagebox.showinfo("Buscar Livros", "Você não digitou o título do livro.")


def show_book_selection(gui):
    title_search = simpledialog.askstring("Buscar Livros", "Digite o título do livro ou parte dele:")
    if title_search:
        results = gui.library.find_book(title_search)
        if results:
            selection_window = Toplevel(gui.master)
            selection_window.title("Selecione um Livro para Alugar")
            window_width = 300
            window_height = 200
            screen_width = selection_window.winfo_screenwidth()
            screen_height = selection_window.winfo_screenheight()
            x = int((screen_width / 2) - (window_width / 2))
            y = int((screen_height / 2) - (window_height / 2))
            selection_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            selection_window.resizable(False, False)
            selection_window.grab_set()

            listbox = Listbox(selection_window, height=6, width=50, border=0)
            listbox.pack(padx=10, pady=10, fill="both", expand=True)

            for book in results:
                listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade:"
                                       f" {book['quantity']}")

            def select_book():
                selected_book = listbox.curselection()
                if selected_book:
                    selected_book = results[selected_book[0]]
                    tenant_name = simpledialog.askstring("Alugar Livro", "Digite o seu nome:")
                    room_number = simpledialog.askstring("Alugar Livro", "Digite o número da sua sala"
                                                                         " ou função:")
                    if tenant_name and room_number:
                        result = gui.library.rent_book(selected_book['title'], selected_book['author'],
                                                       tenant_name, room_number.upper())
                        messagebox.showinfo("Resultado", result)
                        selection_window.destroy()
                        gui.switch_frame(TenantFunctions)

            Button(selection_window, text="Selecionar Livro", command=select_book).pack(pady=10)
        else:
            messagebox.showinfo("Buscar Livros", "Nenhum livro encontrado.")
    else:
        messagebox.showinfo("Buscar Livros", "Você não digitou o título do livro.")


def return_book(gui):
    tenant_name = simpledialog.askstring("Devolver Livro", "Digite o seu nome:")
    if tenant_name:
        result = gui.library.return_book(tenant_name)
        messagebox.showinfo("Resultado", result)


def run_gui():
    root = tk.Tk()
    LibraryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
