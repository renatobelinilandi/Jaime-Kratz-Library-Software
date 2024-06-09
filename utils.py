import pytz
from datetime import datetime

log_file = 'library_log.txt'
admin_password = '123'

def write_to_log(action):
    action_ptbr = translate_action_to_portuguese(action)
    br_tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(br_tz)
    with open(log_file, 'a') as file:
        file.write(f"{now.strftime('%d/%m/%Y - %H:%M')} - {action_ptbr}\n")

def translate_action_to_portuguese(action):
    translations = {
        "Updated quantity for existing book": "Quantidade atualizada para livro existente",
        "Added new book": "Livro novo adicionado",
        "Added units to book": "Unidades adicionadas ao livro",
        "Removed one copy of book": "Uma cópia do livro removida",
        "Removed complete book": "Livro removido completamente",
        "Removed units from book": "Unidades removidas do livro",
        "Rented book": "Livro alugado",
        "Returned book": "Livro devolvido",
        "Renewed loan for book": "Empréstimo do livro renovado",
        "Admin password changed": "Senha do administrador alterada",
        "to": "para",
        "by": "por",
        "for another 14 days": "por mais 14 dias",
        "is overdue": "está atrasado",
        "checked out by": "emprestado por"
    }
    for key, value in translations.items():
        action = action.replace(key, value)
    return action

def center_window(window, window_width, window_height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
