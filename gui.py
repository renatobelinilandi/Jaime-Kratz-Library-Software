import os
import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, Listbox, OptionMenu, StringVar, Text, Scrollbar, Frame
from library import Library
from utils import write_to_log, admin_password, center_window, log_file

# Estilos e cores
background_color = '#f0f0f0'
text_color = '#333'
accent_color = '#FFB347'
result_background_color = '#ffffff'
result_border_color = '#FFB347'

# Atualiza a fonte para Segoe UI
main_button_style = {
    'font': ('Segoe UI', 14),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 400,
    'height': 60
}
button_style = {
    'font': ('Segoe UI', 12),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 400,
    'height': 40
}
label_style = {
    'font': ('Segoe UI', 16, 'bold'),
    'bg_color': background_color,
    'text_color': text_color
}
small_button_style = {
    'font': ('Segoe UI', 12),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 200,
    'height': 40
}
confirm_button_style = {
    'font': ('Segoe UI', 12),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 200,
    'height': 40
}
mini_button_style = {
    'font': ('Segoe UI', 10),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 200,
    'height': 40
}
result_style = {
    'font': ('Segoe UI', 12),
    'bg_color': result_background_color,
    'text_color': text_color,
    'bd': 2,
    'relief': 'solid',
    'padx': 10,
    'pady': 10,
    'width': 800
}
header_style = {
    'font': ('Segoe UI', 25, 'bold'),
    'bg_color': background_color,
    'text_color': text_color
}
rounded_button_style = {
    'font': ('Segoe UI', 12),
    'fg_color': accent_color,
    'text_color': text_color,
    'width': 300,
    'height': 40,
    'border_width': 0
}

class LibraryGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Gerenciamento de Biblioteca")
        self.master.minsize(800, 600)
        self.master.bind("<Configure>", self.on_resize)
        self.library = Library()
        self.frame = None
        self.switch_frame(MainScreens)
        center_window(self.master, 800, 600)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.frame is not None:
            self.frame.destroy()
        self.frame = new_frame
        self.frame.pack(expand=True, fill='both')

    def on_resize(self, event):
        self.adjust_layout(event.width, event.height)

    def adjust_layout(self, width, height):
        if self.frame:
            for widget in self.frame.winfo_children():
                if isinstance(widget, (ctk.CTkButton, ctk.CTkLabel)):
                    font_size = max(10, min(14, width // 50))
                    widget.configure(font=('Segoe UI', font_size))

class MainScreens(ctk.CTkFrame):
    def __init__(self, gui):
        super().__init__(gui.master)
        self.gui = gui
        title = ctk.CTkLabel(self, text="Biblioteca Jaime Kratz", **header_style)
        title.pack(pady=20)

        tenant_button = ctk.CTkButton(self, text="Área do Locatário", command=lambda: gui.switch_frame(TenantFunctions), **rounded_button_style)
        tenant_button.pack(pady=10)

        admin_button = ctk.CTkButton(self, text="Painel de Administração", command=lambda: admin_login(gui), **rounded_button_style)
        admin_button.pack(pady=10)

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.adjust_layout(event.width, event.height)

    def adjust_layout(self, width, height):
        for widget in self.winfo_children():
            if isinstance(widget, (ctk.CTkButton, ctk.CTkLabel)):
                font_size = max(10, min(14, width // 50))
                widget.configure(font=('Segoe UI', font_size))

class TenantFunctions(ctk.CTkFrame):
    def __init__(self, gui):
        super().__init__(gui.master)
        header = ctk.CTkLabel(self, text="Área do Locatário", **header_style)
        header.pack(pady=40)

        search_button = ctk.CTkButton(
            self,
            text="Buscar Livros",
            command=lambda: search_books(gui),
            **rounded_button_style
        )
        rent_button = ctk.CTkButton(
            self,
            text="Alugar Livro",
            command=lambda: check_and_rent_book(gui),
            **rounded_button_style
        )
        renew_button = ctk.CTkButton(
            self,
            text="Renovar Aluguel",
            command=lambda: renew_loan_gui(gui),
            **rounded_button_style
        )
        return_button = ctk.CTkButton(
            self,
            text="Devolver Livro",
            command=lambda: return_book(gui),
            **rounded_button_style
        )
        back_button = ctk.CTkButton(
            self,
            text="Voltar ao Principal",
            command=lambda: gui.switch_frame(MainScreens),
            **rounded_button_style
        )

        for button in [
            search_button,
            rent_button,
            renew_button,
            return_button,
            back_button
        ]:
            button.pack(pady=10)

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.adjust_layout(event.width, event.height)

    def adjust_layout(self, width, height):
        for widget in self.winfo_children():
            if isinstance(widget, (ctk.CTkButton, ctk.CTkLabel)):
                font_size = max(10, min(14, width // 50))
                widget.configure(font=('Segoe UI', font_size))

class AdminPanel(ctk.CTkFrame):
    def __init__(self, gui):
        super().__init__(gui.master)
        header = ctk.CTkLabel(self, text="Painel de Administração", **header_style)
        header.pack(pady=20)

        buttons = [
            ("Adicionar Livro", lambda: add_book(gui)),
            ("Remover Livro", lambda: remove_book(gui)),
            ("Buscar Aluguéis Ativos", lambda: search_active_loans(gui)),
            ("Ver Livros em Atraso", lambda: view_overdue_books(gui)),
            ("Trocar Senha de Admin", lambda: change_admin_password(gui)),
            ("Visualizar Histórico de Ações", lambda: view_log(gui)),
            ("Voltar ao Principal", lambda: gui.switch_frame(MainScreens))
        ]

        self.button_widgets = []
        for text, command in buttons:
            button = ctk.CTkButton(self, text=text, command=command, **rounded_button_style)
            button.pack(pady=10, padx=20, anchor='center')
            self.button_widgets.append(button)

        self.bind("<Configure>", self.resize_buttons)

    def resize_buttons(self, event):
        max_width = 25
        max_height = 3
        max_font_size = 12
        min_width = 15
        min_height = 1
        min_font_size = 8

        new_width = min(max_width, max(min_width, int(event.width / 40)))
        new_height = min(max_height, max(min_height, int(event.height / 100)))
        new_font_size = min(max_font_size, max(min_font_size, int(event.width / 80)))

        for button in self.button_widgets:
            button.configure(
                width=new_width,
                height=new_height,
                font=('Segoe UI', new_font_size),
                padx=10
            )

def admin_login(gui):
    password = simpledialog.askstring("Login de Admin", "Digite a senha:", show='*')
    if password == admin_password:
        gui.switch_frame(AdminPanel)
    else:
        messagebox.showerror("Erro", "Senha incorreta.")

def change_admin_password(gui):
    def change_password():
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()
        if new_password == confirm_password:
            global admin_password
            admin_password = new_password
            write_to_log("Senha do administrador alterada")
            messagebox.showinfo("Sucesso", "Senha de administrador alterada com sucesso.")
            form_window.destroy()
        else:
            messagebox.showerror("Erro", "As senhas não coincidem.")

    form_window = Toplevel(gui.master)
    form_window.title("Trocar Senha de Admin")
    window_width = 400
    window_height = 200
    center_window(form_window, window_width, window_height)
    form_window.resizable(False, False)
    form_window.grab_set()
    form_window.focus_set()
    form_window.lift()

    ctk.CTkLabel(form_window, text="Nova Senha:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    new_password_entry = ctk.CTkEntry(form_window, font=('Segoe UI', 12), show='*')
    new_password_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(form_window, text="Confirme a Senha:", **label_style).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    confirm_password_entry = ctk.CTkEntry(form_window, font=('Segoe UI', 12), show='*')
    confirm_password_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkButton(form_window, text="Trocar Senha", command=change_password, **button_style).grid(row=2, column=0, columnspan=2, pady=20)
    form_window.wait_window()

def add_book(gui):
    response = messagebox.askyesno("Adicionar Livro", "Deseja adicionar um livro novo?")
    if response:
        add_book_form(gui)
    else:
        title = simpledialog.askstring("Adicionar Unidades", "Digite o título do livro para adicionar unidades:")
        if title:
            books_found = gui.library.find_book(title)
            if books_found:
                show_book_selection_for_units(gui, books_found)
            else:
                messagebox.showinfo("Erro", "Livro não encontrado.")
        else:
            messagebox.showinfo("Adicionar Unidades", "Você não digitou o título do livro.")

def show_book_selection_for_units(gui, books_found):
    selection_window = Toplevel(gui.master)
    selection_window.title("Selecione um Livro para Adicionar Unidades")
    selection_window.minsize(400, 300)
    center_window(selection_window, 400, 300)
    selection_window.grab_set()
    selection_window.focus_set()
    selection_window.lift()

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

    ctk.CTkButton(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()

def add_book_form(gui):
    form_window = Toplevel(gui.master)
    form_window.title("Adicionar Livro")
    form_window.minsize(500, 500)
    center_window(form_window, 500, 500)
    form_window.resizable(False, False)
    form_window.grab_set()
    form_window.focus_set()
    form_window.lift()

    genres = [
        "Ficção - Romance", "Ficção - Fantasia", "Ficção - Ficção Científica",
        "Ficção - Suspense e Terror", "Não Ficção - Autoajuda",
        "Não Ficção - Biografia", "Não Ficção - História",
        "Não Ficção - Ciência e Tecnologia"
    ]

    def submit_form():
        title = title_entry.get()
        author = author_entry.get()
        quantity = int(quantity_entry.get())
        genre = genre_var.get()

        if title and author and quantity and genre:
            if messagebox.askokcancel("Confirmar Adição", f"Você está prestes a adicionar o livro '{title}' com {quantity} unidades e gênero '{genre}'. Tem certeza?"):
                result = gui.library.add_book(title, author, quantity, genre)
                messagebox.showinfo("Adição de Livro", result)
                form_window.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

    ctk.CTkLabel(form_window, text="Título:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    title_entry = ctk.CTkEntry(form_window, font=('Segoe UI', 12))
    title_entry.grid(row=0, column=1, padx=10, pady=10)
    title_entry.focus_set()

    ctk.CTkLabel(form_window, text="Autor:", **label_style).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    author_entry = ctk.CTkEntry(form_window, font=('Segoe UI', 12))
    author_entry.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(form_window, text="Quantidade:", **label_style).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    quantity_entry = ctk.CTkEntry(form_window, font=('Segoe UI', 12))
    quantity_entry.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(form_window, text="Gênero:", **label_style).grid(row=3, column=0, padx=10, pady=10, sticky='e')
    genre_var = StringVar()
    genre_menu = OptionMenu(form_window, genre_var, *genres)
    genre_menu.grid(row=3, column=1, padx=10, pady=10)

    ctk.CTkButton(form_window, text="Adicionar Livro", command=submit_form, **button_style).grid(row=4, column=0, columnspan=2, pady=20)
    form_window.wait_window()

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
        selection_window.minsize(400, 300)
        center_window(selection_window, 400, 300)
        selection_window.grab_set()
        selection_window.focus_set()
        selection_window.lift()

        listbox = Listbox(selection_window, height=10, width=60, border=0)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)

        for book in books_found:
            listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade: {book['quantity']}")

        def select_book():
            selected_index = listbox.curselection()
            if selected_index:
                selected_book = books_found[selected_index[0]]
                confirm_removal(gui, selected_book, selection_window)

        ctk.CTkButton(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
        selection_window.wait_window()

    def confirm_removal(gui, selected_book, parent_window):
        parent_window.destroy()
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
        units_window.minsize(400, 200)
        center_window(units_window, 400, 200)
        units_window.grab_set()
        units_window.focus_set()
        units_window.lift()

        ctk.CTkLabel(units_window, text="Quantas unidades deseja remover?", **label_style).pack(pady=20)

        quantity_var = tk.IntVar(value=1)
        spinbox = tk.Spinbox(units_window, from_=1, to=selected_book['quantity'], textvariable=quantity_var, font=('Segoe UI', 12))
        spinbox.pack(pady=10)

        def confirm_units_removal():
            units = quantity_var.get()
            if messagebox.askokcancel("Confirmar Remoção", f"Você está prestes a remover {units} unidades do livro '{selected_book['title']}'. Tem certeza?"):
                result = gui.library.remove_units(selected_book['title'], units)
                messagebox.showinfo("Remoção de Unidades", result)
                units_window.destroy()

        ctk.CTkButton(units_window, text="Remover Unidades", command=confirm_units_removal, **button_style).pack(pady=20)

    search_book_to_remove()

def check_and_rent_book(gui):
    def show_dialog():
        dialog = Toplevel(gui.master)
        dialog.title("Alugar Livro")
        dialog.minsize(400, 200)
        center_window(dialog, 400, 200)
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()

        content_frame = ctk.CTkFrame(dialog, fg_color=background_color)
        content_frame.pack(expand=True, fill='both')

        def reset_dialog():
            for widget in content_frame.winfo_children():
                widget.destroy()

        def select_role():
            reset_dialog()
            ctk.CTkLabel(content_frame, text="Selecione a sua função:", **label_style).pack(pady=20)
            ctk.CTkButton(content_frame, text="Aluno", command=lambda: get_name("Aluno"), **small_button_style).pack(pady=10)
            ctk.CTkButton(content_frame, text="Funcionário", command=lambda: get_name("Funcionário"), **small_button_style).pack(pady=10)

        def get_name(role):
            reset_dialog()
            ctk.CTkLabel(content_frame, text="Digite o seu nome:", **label_style).pack(pady=10)
            name_entry = ctk.CTkEntry(content_frame, font=('Segoe UI', 12))
            name_entry.pack(pady=10)
            name_entry.focus_set()

            def confirm_name(event=None):
                name = name_entry.get().upper()
                if name:
                    if role == "Aluno":
                        get_series(name, role)
                    else:
                        get_book_title(name, role)

            ctk.CTkButton(content_frame, text="Confirmar", command=confirm_name, **confirm_button_style).pack(pady=20)
            name_entry.bind("<Return>", confirm_name)

        def get_series(name, role):
            reset_dialog()
            ctk.CTkLabel(content_frame, text="Digite a sua série (Ex: 3B):", **label_style).pack(pady=10)
            series_entry = ctk.CTkEntry(content_frame, font=('Segoe UI', 12))
            series_entry.pack(pady=10)
            series_entry.focus_set()

            def confirm_series(event=None):
                series = series_entry.get().upper()
                if series:
                    get_book_title(name, f"{role} - {series}")

            ctk.CTkButton(content_frame, text="Confirmar", command=confirm_series, **confirm_button_style).pack(pady=20)
            series_entry.bind("<Return>", confirm_series)

        def get_book_title(name, role):
            reset_dialog()
            ctk.CTkLabel(content_frame, text="Digite o título do livro:", **label_style).pack(pady=10)
            title_entry = ctk.CTkEntry(content_frame, font=('Segoe UI', 12))
            title_entry.pack(pady=10)
            title_entry.focus_set()

            def confirm_title(event=None):
                title = title_entry.get()
                if title:
                    books_found = gui.library.find_book(title)
                    if books_found:
                        show_book_selection(dialog, books_found, name, role, gui.library)
                        dialog.destroy()
                    else:
                        messagebox.showerror("Erro de Aluguel", "Livro não encontrado.")

            ctk.CTkButton(content_frame, text="Confirmar", command=confirm_title, **confirm_button_style).pack(pady=20)
            title_entry.bind("<Return>", confirm_title)

        select_role()
        dialog.wait_window()

    show_dialog()

def show_book_selection(parent_window, books_found, tenant_name, room_number, library):
    selection_window = Toplevel(parent_window)
    selection_window.title("Selecione um Livro para Alugar")
    selection_window.minsize(400, 300)
    center_window(selection_window, 400, 300)
    selection_window.grab_set()
    selection_window.focus_set()
    selection_window.lift()

    listbox = Listbox(selection_window, height=10, width=60, border=0)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    for book in books_found:
        listbox.insert(tk.END, f"{book['title']} - {book['author']} - Quantidade: {book['quantity']}")

    def select_book():
        selected_index = listbox.curselection()
        if selected_index:
            selected_book = books_found[selected_index[0]]
            result = library.rent_book(
                selected_book['title'],
                selected_book['author'],
                tenant_name,
                room_number
            )
            messagebox.showinfo("Resultado", result)
            selection_window.destroy()

    ctk.CTkButton(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()

def view_overdue_books(gui):
    overdue_books = gui.library.find_overdue_books()
    if overdue_books:
        show_books_in_window(gui, "Livros em Atraso", overdue_books)
    else:
        show_info_window(gui, "Livros em Atraso", "Nenhum livro em atraso encontrado.")

def search_active_loans(gui):
    search_query = simpledialog.askstring(
        "Buscar Empréstimos Ativos",
        "Digite o nome, parte do título do livro, ou número da sala/função:"
    )
    if search_query:
        active_loans = gui.library.find_active_loans_by_name_or_title(search_query)
        if active_loans:
            show_books_in_window(gui, "Empréstimos Ativos", active_loans)
        else:
            show_info_window(gui, "Empréstimos Ativos", "Nenhum empréstimo correspondente encontrado.")
    else:
        messagebox.showinfo("Buscar Empréstimos Ativos", "Você não digitou uma pesquisa.")

def search_books(gui):
    search_window = Toplevel(gui.master)
    search_window.title("Buscar Livros")
    search_window.minsize(600, 300)
    center_window(search_window, 600, 300)
    search_window.grab_set()
    search_window.focus_set()
    search_window.lift()

    genres = [
        "Qualquer", "Ficção - Romance", "Ficção - Fantasia",
        "Ficção - Ficção Científica", "Ficção - Suspense e Terror",
        "Não Ficção - Autoajuda", "Não Ficção - Biografia",
        "Não Ficção - História", "Não Ficção - Ciência e Tecnologia"
    ]

    def perform_search():
        search_text = title_author_entry.get()
        genre_search = genre_var.get()

        if search_text:
            results = gui.library.find_books_by_title_author_and_genre(search_text, genre_search)
            if results:
                show_books_in_window(gui, "Resultados da Busca", results)
            else:
                show_info_window(gui, "Resultados da Busca", "Nenhum livro encontrado.")
        else:
            messagebox.showinfo("Buscar Livros", "Você não digitou o título ou autor do livro.")

    ctk.CTkLabel(search_window, text="Buscar por Título ou Autor:", **label_style).grid(
        row=0, column=0, padx=10, pady=10, sticky='e'
    )
    title_author_entry = ctk.CTkEntry(search_window, font=('Segoe UI', 12))
    title_author_entry.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(search_window, text="Buscar por Gênero:", **label_style).grid(
        row=1, column=0, padx=10, pady=10, sticky='e'
    )
    genre_var = StringVar()
    genre_menu = OptionMenu(search_window, genre_var, *genres)
    genre_menu.grid(row=1, column=1, padx=10, pady=10)
    genre_var.set(genres[0])

    ctk.CTkButton(search_window, text="OK", command=perform_search, **button_style).grid(
        row=2, column=0, columnspan=2, padx=10, pady=20
    )
    search_window.wait_window()

def show_books_in_window(gui, title, books):
    info_window = Toplevel(gui.master)
    info_window.title(title)
    info_window.minsize(800, 600)
    center_window(info_window, 800, 600)
    info_window.grab_set()
    info_window.focus_set()
    info_window.lift()

    canvas = ctk.CTkCanvas(info_window)
    scrollbar = Scrollbar(info_window, command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for book in books:
        book_info = (
            f"Título: {book['title']}\n"
            f"Autor: {book['author']}\n"
            f"Gênero: {book.get('genre', 'N/A')}\n"
        )
        if 'quantity' in book:
            book_info += f"Quantidade: {book['quantity']}\n"
        if 'tenant_name' in book and 'room_number' in book:
            book_info += (
                f"Locatário: {book['tenant_name']}\n"
                f"Função: {book['room_number']}\n"
                f"Data de Devolução: {book.get('return_date', 'N/A')}\n"
                f"Aluguéis Consecutivos: {book.get('consecutive_loans', 0)}\n"
            )

        result_label = ctk.CTkLabel(scrollable_frame, text=book_info, **result_style)
        result_label.pack(fill='both', pady=5, padx=5)

    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    info_window.update_idletasks()
    info_window.wait_window()

def show_info_window(gui, title, content, show_clear_button=False):
    info_window = Toplevel(gui.master)
    info_window.title(title)
    info_window.minsize(600, 400)
    if show_clear_button:
        info_window.geometry("1280x720")
    else:
        info_window.geometry("600x400")
    center_window(info_window, 600, 400)
    info_window.resizable(False, False)
    info_window.grab_set()
    info_window.focus_set()
    info_window.lift()

    text_area = ctk.CTkTextbox(info_window, wrap='word', font=('Segoe UI', 12))
    scrollbar = Scrollbar(info_window, command=text_area.yview)
    text_area.configure(yscrollcommand=scrollbar.set)
    text_area.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    text_area.insert('1.0', content)
    text_area.see('1.0')

    if show_clear_button:
        def clear_log():
            password = simpledialog.askstring("Senha de Admin", "Digite a senha de administrador para limpar o histórico:", show='*')
            if password == admin_password:
                with open(log_file, 'w') as file:
                    file.write('')
                messagebox.showinfo("Sucesso", "Histórico apagado com sucesso.")
                info_window.destroy()
            else:
                messagebox.showerror("Erro", "Senha incorreta.")

        ctk.CTkButton(info_window, text="Apagar Histórico", command=clear_log, **mini_button_style).pack(pady=10, side='bottom')

    info_window.wait_window()

def view_log(gui):
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            log_content = file.readlines()
        log_content.reverse()
        log_content = ''.join(log_content)
    else:
        log_content = "Nenhum histórico encontrado."

    show_info_window(gui, "Histórico de Ações", log_content, show_clear_button=True)

def renew_loan_gui(gui):
    tenant_name = simpledialog.askstring("Renovar Aluguel", "Digite o seu nome:")
    if tenant_name:
        message, book_title = gui.library.renew_loan(tenant_name)
        if book_title:
            response = messagebox.askyesno("Confirmar Renovação", message)
            if response:
                messagebox.showinfo(
                    "Renovação de Aluguel",
                    f"Aluguel do livro '{book_title}' renovado com sucesso por mais 14 dias."
                )
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
    root = ctk.CTk()
    LibraryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
