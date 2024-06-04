import tkinter as tk
import os
from tkinter import simpledialog, messagebox, Toplevel, Listbox, Entry, Button, Label, Spinbox, Text, Scrollbar
from library import Library
from utils import write_to_log, admin_password, center_window, log_file

background_color = '#f0f0f0'
text_color = '#333'
accent_color = '#FFB347'
main_button_style = {'font': ('JetBrains Mono', 14), 'background': accent_color, 'foreground': text_color, 'width': 40, 'height': 4}
button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 30, 'height': 3}
label_style = {'font': ('JetBrains Mono', 16, 'bold'), 'background': background_color, 'foreground': text_color}
small_button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 20, 'height': 2}
confirm_button_style = {'font': ('JetBrains Mono', 12), 'background': accent_color, 'foreground': text_color, 'width': 20, 'height': 2}
mini_button_style = {'font': ('JetBrains Mono', 10), 'background': accent_color, 'foreground': text_color, 'width': 20, 'height': 2}

class LibraryGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de Gerenciamento de Biblioteca")
        self.master.resizable(True, True)
        self.master.minsize(900, 700)
        self.library = Library()
        self.frame = None
        self.center_window()
        self.switch_frame(MainScreens)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
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

class MainScreens(tk.Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Biblioteca Jaime Kratz", **label_style).pack(pady=40)
        Button(self, text="Área do Locatário", command=lambda: gui.switch_frame(TenantFunctions), **main_button_style).pack(pady=20)
        Button(self, text="Painel de Administração", command=lambda: admin_login(gui), **main_button_style).pack(pady=20)

class AdminPanel(tk.Frame):
    def __init__(self, gui):
        super().__init__(gui.master, bg=background_color)
        Label(self, text="Painel de Administração", **label_style).pack(pady=20)

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
            button = Button(self, text=text, command=command, **button_style)
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
            button.config(width=new_width, height=new_height, font=('JetBrains Mono', new_font_size), padx=10)

class TenantFunctions(tk.Frame):
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
            write_to_log("Admin password changed")
            messagebox.showinfo("Sucesso", "Senha de administrador alterada com sucesso.")
        else:
            messagebox.showerror("Erro", "As senhas não coincidem.")
    else:
        messagebox.showerror("Erro", "Senha atual incorreta.")

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
    window_width = 400
    window_height = 300
    center_window(selection_window, window_width, window_height)
    selection_window.resizable(False, False)
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

    Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()

def add_book_form(gui):
    form_window = Toplevel(gui.master)
    form_window.title("Adicionar Livro")
    window_width = 500
    window_height = 400
    center_window(form_window, window_width, window_height)
    form_window.resizable(False, False)
    form_window.grab_set()
    form_window.focus_set()
    form_window.lift()

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
        window_width = 400
        window_height = 300
        center_window(selection_window, window_width, window_height)
        selection_window.resizable(False, False)
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

        Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
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
        window_width = 400
        window_height = 200
        center_window(units_window, window_width, window_height)
        units_window.resizable(False, False)
        units_window.grab_set()
        units_window.focus_set()
        units_window.lift()

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
    def show_dialog():
        dialog = Toplevel(gui.master)
        dialog.title("Alugar Livro")
        window_width = 400
        window_height = 200
        center_window(dialog, window_width, window_height)
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()

        content_frame = tk.Frame(dialog, bg=background_color)
        content_frame.pack(expand=True, fill='both')

        def reset_dialog():
            for widget in content_frame.winfo_children():
                widget.destroy()

        def select_role():
            reset_dialog()
            Label(content_frame, text="Selecione a sua função:", **label_style).pack(pady=20)
            Button(content_frame, text="Aluno", command=lambda: get_name("Aluno"), **small_button_style).pack(pady=10)
            Button(content_frame, text="Funcionário", command=lambda: get_name("Funcionário"), **small_button_style).pack(pady=10)

        def get_name(role):
            reset_dialog()
            Label(content_frame, text="Digite o seu nome:", **label_style).pack(pady=10)
            name_entry = Entry(content_frame, font=('JetBrains Mono', 12))
            name_entry.pack(pady=10)
            name_entry.focus_set()

            def confirm_name(event=None):
                name = name_entry.get().upper()
                if name:
                    if role == "Aluno":
                        get_series(name, role)
                    else:
                        get_book_title(name, role)

            Button(content_frame, text="Confirmar", command=confirm_name, **confirm_button_style).pack(pady=20)
            name_entry.bind("<Return>", confirm_name)

        def get_series(name, role):
            reset_dialog()
            Label(content_frame, text="Digite a sua série (Ex: 3B):", **label_style).pack(pady=10)
            series_entry = Entry(content_frame, font=('JetBrains Mono', 12))
            series_entry.pack(pady=10)
            series_entry.focus_set()

            def confirm_series(event=None):
                series = series_entry.get().upper()
                if series:
                    get_book_title(name, f"{role} - {series}")

            Button(content_frame, text="Confirmar", command=confirm_series, **confirm_button_style).pack(pady=20)
            series_entry.bind("<Return>", confirm_series)

        def get_book_title(name, role):
            reset_dialog()
            Label(content_frame, text="Digite o título do livro:", **label_style).pack(pady=10)
            title_entry = Entry(content_frame, font=('JetBrains Mono', 12))
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

            Button(content_frame, text="Confirmar", command=confirm_title, **confirm_button_style).pack(pady=20)
            title_entry.bind("<Return>", confirm_title)

        select_role()
        dialog.wait_window()

    show_dialog()

def show_book_selection(parent_window, books_found, tenant_name, room_number, library):
    selection_window = Toplevel(parent_window)
    selection_window.title("Selecione um Livro para Alugar")
    window_width = 400
    window_height = 300
    center_window(selection_window, window_width, window_height)
    selection_window.resizable(False, False)
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
            result = library.rent_book(selected_book['title'], selected_book['author'], tenant_name, room_number)
            messagebox.showinfo("Resultado", result)
            selection_window.destroy()

    Button(selection_window, text="Selecionar Livro", command=select_book, **button_style).pack(pady=10)
    selection_window.wait_window()

def view_overdue_books(gui):
    overdue_books = gui.library.find_overdue_books()
    if overdue_books:
        book_info = '\n'.join([f"\nTítulo: {book['title']} - Escrito por: {book['author']}\nAlugado por: {book['tenant_name']} na sala/função: {book['room_number']}\nDevolução em: {book['return_date']}\nAluguéis consecutivos: {book['consecutive_loans']}\n{'-' * 40}" for book in overdue_books])
    else:
        book_info = "Nenhum livro em atraso encontrado."
    show_info_window(gui, "Livros em Atraso", book_info)

def search_active_loans(gui):
    search_query = simpledialog.askstring("Buscar Empréstimos Ativos", "Digite o nome, parte do título do livro, ou número da sala/função:")
    if search_query:
        active_loans = gui.library.find_active_loans_by_name_or_title(search_query)
        if active_loans:
            loan_info = '\n'.join([f"Título: {loan['title']} - Escrito por: {loan['author']}\nAlugado por: {loan['tenant_name']} na sala/função: {loan['room_number']}\nDevolução em: {loan['return_date']}\nAluguéis consecutivos: {loan['consecutive_loans']}\n{'-' * 40}" for loan in active_loans])
        else:
            loan_info = "Nenhum empréstimo correspondente encontrado."
        show_info_window(gui, "Empréstimos Ativos", loan_info)
    else:
        messagebox.showinfo("Buscar Empréstimos Ativos", "Você não digitou uma pesquisa.")

def search_books(gui):
    title_search = simpledialog.askstring("Buscar Livros", "Digite o título do livro ou parte dele:")
    if title_search:
        results = gui.library.find_book(title_search)
        if results:
            books = '\n'.join([f"\nTítulo: {book['title']} - Escrito por: {book['author']} - Quantidade: {book['quantity']}\n{'-' * 40}" for book in results])
        else:
            books = "Nenhum livro encontrado."
        show_info_window(gui, "Resultados da Busca", books)
    else:
        messagebox.showinfo("Buscar Livros", "Você não digitou o título do livro.")

def show_info_window(gui, title, content, show_clear_button=False):
    info_window = Toplevel(gui.master)
    info_window.title(title)
    window_width = 1280 if show_clear_button else 600
    window_height = 720 if show_clear_button else 400
    center_window(info_window, window_width, window_height)
    info_window.resizable(False, False)
    info_window.grab_set()
    info_window.focus_set()
    info_window.lift()

    text_area = Text(info_window, wrap='word', font=('JetBrains Mono', 12))
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

        clear_button = Button(info_window, text="Apagar Histórico", command=clear_log, **mini_button_style)
        clear_button.pack(pady=10, side='bottom')

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
