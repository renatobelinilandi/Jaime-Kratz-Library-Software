import tkinter as tk
from tkinter import simpledialog, messagebox, Frame, Button, Label, Entry, Toplevel, Listbox, Spinbox
from datetime import datetime, timedelta
import json
import os
import unicodedata

# Colors and styles
background_color = '#f0f0f0'
text_color = '#333'
accent_color = '#FFB347'  # Pastel orange
main_button_style = {'font': ('JetBrains Mono', 14), 'background': accent_color, 'foreground': text_color, 'width': 40, 'height': 4}
button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 30, 'height': 3}
label_style = {'font': ('JetBrains Mono', 16, 'bold'), 'background': background_color, 'foreground': text_color}
small_button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 15, 'height': 2}
large_button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 30, 'height': 3}

# Default admin password
admin_password = "123"

# Function to count consecutive loans of a book by a tenant
def count_consecutive_loans(book, tenant_name):
    count = 0
    for loan in reversed(book['loans']):  # Reverse the list to start from the most recent to the oldest
        if loan['tenant_name'] == tenant_name:
            if loan.get('returned', False):
                break  # Stop counting if a returned loan is found
            count += 1
        else:
            break
    return count

# Function to find all active loans
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
                    'consecutive_loans': self.count_consecutive_loans(book, loan['tenant_name'])
                }
                active_loans.append(loan_info)
    return active_loans

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
        if any(loan for book in self.books for loan in book['loans'] if
               loan['tenant_name'] == tenant_name and not loan['returned']):
            return "Você já tem um livro alugado. Devolva o livro atual antes de alugar um novo."

        for book in self.books:
            if self.remove_accents(book['title']).lower() == self.remove_accents(title).lower() and \
                    self.remove_accents(book['author']).lower() == self.remove_accents(author).lower():
                if book['quantity'] > 0:
                    book['quantity'] -= 1
                    now = datetime.now()
                    loan = {
                        'tenant_name': tenant_name,
                        'room_number': room_number,
                        'return_date': (now + timedelta(days=14)).strftime('%d/%m/%Y'),
                        'returned': False,
                        'rental_start_date': now.strftime('%d/%m/%Y')
                    }
                    book['loans'].append(loan)
                    self.save_data()
                    return "Livro alugado com sucesso."
                return "Todos os exemplares estão alugados."
        return "Livro não encontrado."

    def return_book(self, tenant_name):
        tenant_name = tenant_name.upper()
        book_returned = False
        for book in self.books:
            updated_loans = []
            for loan in book['loans']:
                if loan['tenant_name'] == tenant_name and not loan['returned']:
                    loan['returned'] = True
                    book['quantity'] += 1
                    book_returned = True
                else:
                    updated_loans.append(loan)
            book['loans'] = updated_loans
        if book_returned:
            self.consecutive_loans.pop(tenant_name, None)  # Reset after return
            self.save_data()
            return "Empréstimo devolvido com sucesso."
        return "Nenhum empréstimo ativo encontrado para este locatário."

    def renew_loan(self, tenant_name):
        tenant_name = tenant_name.upper()
        loan_found = False
        for book in self.books:
            for loan in book['loans']:
                if loan['tenant_name'] == tenant_name and not loan['returned']:
                    new_return_date = (datetime.now() + timedelta(days=14)).strftime('%d/%m/%Y')
                    loan['return_date'] = new_return_date
                    loan['consecutive_loans'] = loan.get('consecutive_loans', 0) + 1
                    self.consecutive_loans[tenant_name] = loan['consecutive_loans']
                    self.save_data()
                    loan_found = True
                    return f"Você está renovando o aluguel do livro {book['title']} por mais 14 dias, está certo disso?", \
                        book['title']
        if not loan_found:
            return "Nenhum empréstimo ativo encontrado para este locatário.", None

    def find_overdue_books(self):
        today = datetime.now().date()
        overdue_books = []
        for book in self.books:
            for loan in book['loans']:
                return_date = datetime.strptime(loan['return_date'], '%d/%m/%Y').date()
                if return_date < today and not loan.get('returned', False):
                    loan_info = {
                        'title': book['title'],
                        'author': book['author'],
                        'tenant_name': loan['tenant_name'],
                        'room_number': loan['room_number'],
                        'return_date': loan['return_date'],
                        'consecutive_loans': loan.get('consecutive_loans', 0)
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
                        'consecutive_loans': loan.get('consecutive_loans', 0)
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
        self.master.resizable(True, True)  # Allow the window to be resizable
        self.library = Library()
        self.frame = None
        self.center_window()
        self.switch_frame(MainScreens)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        # Set the window size to a percentage of the screen size
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.master.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = new_frame
        self.frame.pack(expand=True, fill='both')


class MainScreens(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Biblioteca Jaime Kratz", **label_style).pack(pady=40)
        Button(self, text="Área do locatário", command=lambda: gui.switch_frame(TenantFunctions), **main_button_style).pack(pady=20)
        Button(self, text="Painel de Administração", command=lambda: admin_login(gui), **main_button_style).pack(pady=20)


class AdminPanel(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Painel de Administração", **label_style).pack(pady=40)
        Button(self, text="Adicionar Livro", command=lambda: add_book(gui), **button_style).pack(pady=10)
        Button(self, text="Remover Livro", command=lambda: remove_book(gui), **button_style).pack(pady=10)
        Button(self, text="Buscar Aluguéis Ativos", command=lambda: search_active_loans(gui), **button_style).pack(pady=10)
        Button(self, text="Ver Livros em Atraso", command=lambda: view_overdue_books(gui), **button_style).pack(pady=10)
        Button(self, text="Trocar Senha de Admin", command=lambda: change_admin_password(gui), **button_style).pack(pady=10)
        Button(self, text="Voltar ao Principal", command=lambda: gui.switch_frame(MainScreens), **large_button_style).pack(pady=30)


class TenantFunctions(Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Área do Locatário", **label_style).pack(pady=40)
        Button(self, text="Buscar Livros", command=lambda: search_books(gui), **button_style).pack(pady=10)
        Button(self, text="Alugar Livro", command=lambda: check_and_rent_book(gui), **button_style).pack(pady=10)
        Button(self, text="Renovar Aluguel", command=lambda: renew_loan_gui(gui), **button_style).pack(pady=10)
        Button(self, text="Devolver Livro", command=lambda: return_book(gui), **button_style).pack(pady=10)
        Button(self, text="Voltar ao Principal", command=lambda: gui.switch_frame(MainScreens), **button_style).pack(pady=30)


def admin_login(gui):
    global admin_password
    password = simpledialog.askstring("Login de Admin", "Digite a senha:", show='*')
    if password == admin_password:
        gui.switch_frame(AdminPanel)
    else:
        messagebox.showerror("Erro", "Senha incorreta.")


def change_admin_password(gui):
    global admin_password
    current_password = simpledialog.askstring("Trocar Senha de Admin", "Digite a senha atual:", show='*')
    if current_password == admin_password:
        new_password = simpledialog.askstring("Trocar Senha de Admin", "Digite a nova senha:", show='*')
        confirm_password = simpledialog.askstring("Trocar Senha de Admin", "Confirme a nova senha:", show='*')
        if new_password == confirm_password:
            admin_password = new_password
            messagebox.showinfo("Sucesso", "Senha de administrador alterada com sucesso.")
        else:
            messagebox.showerror("Erro", "As senhas não coincidem.")
    else:
        messagebox.showerror("Erro", "Senha atual incorreta.")


def add_book(gui):
    response = messagebox.askyesno("Adicionar Livro", "Deseja adicionar um livro novo?")
    if response:
        # Add a new book
        add_book_form(gui)
    else:
        # Add units to an existing book
        title = simpledialog.askstring("Adicionar Unidades", "Digite o título do livro para adicionar unidades:")
        if title:
            books_found = gui.library.find_book(title)
            if books_found:
                # New window for book selection
                show_book_selection_for_units(gui, books_found)
            else:
                messagebox.showinfo("Erro", "Livro não encontrado.")
        else:
            messagebox.showinfo("Adicionar Unidades", "Você não digitou o título do livro.")


def center_window(window, window_width, window_height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")


def show_book_selection_for_units(gui, books_found):
    selection_window = Toplevel(gui.master)
    selection_window.title("Selecione um Livro para Adicionar Unidades")
    window_width = 400
    window_height = 300
    center_window(selection_window, window_width, window_height)
    selection_window.resizable(False, False)
    selection_window.grab_set()
    selection_window.focus_set()
    selection_window.lift()  # Bring to the front

    listbox = Listbox(selection_window, height=10, width=60, border=0)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    for book in books_found:
        listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade: {book['quantity']}")

    def select_book():
        selected_index = listbox.curselection()
        if selected_index:
            selected_book = books_found[selected_index[0]]
            units = simpledialog.askinteger("Adicionar Unidades", "Quantas unidades você deseja adicionar?", minvalue=1)
            if units:
                if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar {units} unidades ao livro '{selected_book['title']}'. Tem certeza?"):
                    result = gui.library.add_units(selected_book['title'], units)
                    messagebox.showinfo("Adição de Unidades", result)
                    selection_window.destroy()

    Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()  # Wait for the window to be closed


def add_book_form(gui):
    form_window = Toplevel(gui.master)
    form_window.title("Adicionar Livro")
    window_width = 500
    window_height = 400
    center_window(form_window, window_width, window_height)
    form_window.resizable(False, False)
    form_window.grab_set()
    form_window.focus_set()
    form_window.lift()  # Bring to the front

    def submit_form():
        title = title_entry.get()
        author = author_entry.get()
        quantity = int(quantity_entry.get())

        if title and author and quantity:
            if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar o livro '{title}' com {quantity} unidades. Tem certeza?"):
                result = gui.library.add_book(title, author, quantity)
                messagebox.showinfo("Adição de Livro", result)
                form_window.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    Label(form_window, text="Título:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    title_entry = Entry(form_window, font=('JetBrains Mono', 12))
    title_entry.grid(row=0, column=1, padx=10, pady=10)
    title_entry.focus_set()

    Label(form_window, text="Autor:", **label_style).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    author_entry = Entry(form_window, font=('JetBrains Mono', 12))
    author_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(form_window, text="Quantidade:", **label_style).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    quantity_entry = Entry(form_window, font=('JetBrains Mono', 12))
    quantity_entry.grid(row=2, column=1, padx=10, pady=10)

    Button(form_window, text="Adicionar Livro", command=submit_form, **button_style).grid(row=3, column=0, columnspan=2, pady=20)
    form_window.wait_window()  # Wait for the window to be closed


def remove_book(gui):
    def search_book_to_remove():
        title = simpledialog.askstring("Remover Livro", "Digite o título do livro que deseja remover:")
        if title:
            books_found = gui.library.find_book(title)
            if books_found:
                show_book_selection_for_removal(gui, books_found)
            else:
                messagebox.showinfo("Erro", "Livro não encontrado.")
        else:
            messagebox.showinfo("Remover Livro", "Você não digitou o nome do livro.")

    def show_book_selection_for_removal(gui, books_found):
        selection_window = Toplevel(gui.master)
        selection_window.title("Selecione um Livro para Remover")
        window_width = 400
        window_height = 300
        center_window(selection_window, window_width, window_height)
        selection_window.resizable(False, False)
        selection_window.grab_set()
        selection_window.focus_set()
        selection_window.lift()  # Bring to the front

        listbox = Listbox(selection_window, height=10, width=60, border=0)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)

        for book in books_found:
            listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade: {book['quantity']}")

        def select_book():
            selected_index = listbox.curselection()
            if selected_index:
                selected_book = books_found[selected_index[0]]
                confirm_removal(gui, selected_book, selection_window)

        Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
        selection_window.wait_window()  # Wait for the window to be closed

    def confirm_removal(gui, selected_book, parent_window):
        parent_window.destroy()  # Close the previous window
        response = messagebox.askyesno("Remover Livro", "Deseja remover o livro completamente?")
        if response:
            if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover o livro '{selected_book['title']}' completamente. Tem certeza?"):
                result = gui.library.remove_complete_book(selected_book['title'])
                messagebox.showinfo("Remoção de Livro", result)
        else:
            remove_units(gui, selected_book)

    def remove_units(gui, selected_book):
        units_window = Toplevel(gui.master)
        units_window.title("Remover Unidades")
        window_width = 400
        window_height = 200
        center_window(units_window, window_width, window_height)
        units_window.resizable(False, False)
        units_window.grab_set()
        units_window.focus_set()
        units_window.lift()  # Bring to the front

        Label(units_window, text="Quantas unidades deseja remover?", **label_style).pack(pady=20)

        quantity_var = tk.IntVar(value=1)
        spinbox = Spinbox(units_window, from_=1, to=selected_book['quantity'], textvariable=quantity_var, font=('JetBrains Mono', 12))
        spinbox.pack(pady=10)

        def confirm_units_removal():
            units = quantity_var.get()
            if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover {units} unidades do livro '{selected_book['title']}'. Tem certeza?"):
                result = gui.library.remove_units(selected_book['title'], units)
                messagebox.showinfo("Remoção de Unidades", result)
                units_window.destroy()

        Button(units_window, text="Remover Unidades", command=confirm_units_removal, **button_style).pack(pady=20)

    search_book_to_remove()


def check_and_rent_book(gui):
    def select_role():
        role_window = Toplevel(gui.master)
        role_window.title("Selecionar Função")
        window_width = 400
        window_height = 200
        center_window(role_window, window_width, window_height)
        role_window.resizable(False, False)
        role_window.grab_set()
        role_window.focus_set()
        role_window.lift()  # Bring to the front

        Label(role_window, text="Selecione a sua função:", **label_style).pack(pady=20)

        def select_role(role):
            role_window.destroy()
            get_name(role)

        Button(role_window, text="Aluno", command=lambda: select_role("Aluno"), **small_button_style).pack(pady=10)
        Button(role_window, text="Funcionário", command=lambda: select_role("Funcionário"), **small_button_style).pack(pady=10)

        role_window.wait_window()

    def get_name(role):
        name = simpledialog.askstring("Alugar Livro", "Digite o seu nome:")
        if name:
            name = name.upper()
            if role == "Aluno":
                get_series(name, role)
            else:
                get_book_title(name, role)

    def get_series(name, role):
        series = simpledialog.askstring("Alugar Livro", "Digite a sua série (Ex: 3B):")
        if series:
            get_book_title(name, f"{role} - {series.upper()}")

    def get_book_title(name, role):
        title = simpledialog.askstring("Alugar Livro", "Digite o título do livro que deseja alugar:")
        if title:
            books_found = gui.library.find_book(title)
            if books_found:
                show_book_selection(gui, books_found, name, role)
            else:
                messagebox.showerror("Erro de Aluguel", "Livro não encontrado.")
        else:
            messagebox.showinfo("Aluguel de Livro", "Você não digitou o título do livro.")

    select_role()


def view_overdue_books(gui):
    overdue_books = gui.library.find_overdue_books()
    if overdue_books:
        book_info = '\n'.join([f"\nTítulo: {book['title']} - Escrito por:"
                               f" {book['author']}\nAlugado por:"
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


def show_book_selection(gui, books_found, tenant_name, room_number):
    selection_window = Toplevel(gui.master)
    selection_window.title("Selecione um Livro para Alugar")
    window_width = 400
    window_height = 300
    center_window(selection_window, window_width, window_height)
    selection_window.resizable(False, False)
    selection_window.grab_set()
    selection_window.focus_set()
    selection_window.lift()  # Bring to the front

    listbox = Listbox(selection_window, height=10, width=60, border=0)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    for book in books_found:
        listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade: {book['quantity']}")

    def select_book():
        selected_index = listbox.curselection()
        if selected_index:
            selected_book = books_found[selected_index[0]]
            result = gui.library.rent_book(selected_book['title'], selected_book['author'], tenant_name, room_number)
            messagebox.showinfo("Resultado", result)
            selection_window.destroy()

    Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()  # Wait for the window to be closed


def renew_loan_gui(gui):
    tenant_name = simpledialog.askstring("Renovar Aluguel", "Digite o seu nome:")
    if tenant_name:
        message, book_title = gui.library.renew_loan(tenant_name)
        if book_title:  # If a book was found and renewal is possible
            response = messagebox.askyesno("Confirmar Renovação", message)
            if response:
                messagebox.showinfo("Renovação de Aluguel", f"Aluguel do livro '{book_title}' renovado com sucesso por mais 14 dias.")
            else:
                messagebox.showinfo("Renovação de Aluguel", "Renovação cancelada.")
        else:
            messagebox.showinfo("Renovação de Aluguel", message)


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
