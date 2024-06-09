import json
import os
from datetime import datetime, timedelta
import unicodedata
from utils import write_to_log, log_file

class Library:
    def __init__(self):
        self.data_file = 'library_data.json'
        self.books = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            if os.path.getsize(self.data_file) > 0:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            else:
                return []
        else:
            with open(self.data_file, 'w') as file:
                json.dump([], file, indent=4)
            return []

    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.books, file, indent=4)

    def add_book(self, title, author, quantity, genre):
        for book in self.books:
            if self._normalize_text(book['title']) == self._normalize_text(title) and \
               self._normalize_text(book['author']) == self._normalize_text(author):
                book['quantity'] += quantity
                self.save_data()
                write_to_log(f"Updated quantity for existing book: {title} by {author}, new quantity: {book['quantity']}")
                return "Quantidade atualizada para livro existente."
        self.books.append({'title': title, 'author': author, 'quantity': quantity, 'genre': genre, 'loans': []})
        self.save_data()
        write_to_log(f"Added new book: {title} by {author}, quantity: {quantity}, genre: {genre}")
        return "Livro novo adicionado."

    def add_units(self, title, units):
        for book in self.books:
            if self._normalize_text(book['title']) == self._normalize_text(title):
                book['quantity'] += units
                self.save_data()
                write_to_log(f"Added {units} units to book: {title}")
                return f"Adicionadas {units} unidades ao livro '{title}'."
        return "Livro não encontrado."

    def remove_book(self, title, author):
        for book in self.books:
            if self._normalize_text(book['title']) == self._normalize_text(title) and \
               self._normalize_text(book['author']) == self._normalize_text(author):
                if book['quantity'] > 0:
                    book['quantity'] -= 1
                    self.save_data()
                    write_to_log(f"Removed one copy of book: {title} by {author}")
                    return "Livro removido com sucesso."
                return "Todas as cópias já foram removidas."
        return "Livro não encontrado."

    def remove_complete_book(self, title):
        self.books = [book for book in self.books if self._normalize_text(book['title']) != self._normalize_text(title)]
        self.save_data()
        write_to_log(f"Removed complete book: {title}")
        return "Livro removido completamente."

    def remove_units(self, title, units):
        for book in self.books:
            if self._normalize_text(book['title']) == self._normalize_text(title):
                if book['quantity'] >= units:
                    book['quantity'] -= units
                    self.save_data()
                    write_to_log(f"Removed {units} units from book: {title}")
                    return f"Removidas {units} unidades do livro '{title}'."
        return "Quantidade insuficiente para remoção ou livro não encontrado."

    def find_book(self, title):
        title = self._normalize_text(title)
        return [book for book in self.books if title in self._normalize_text(book['title'])]

    def find_books_by_title_author_and_genre(self, search_text, genre):
        search_text = self._normalize_text(search_text)
        genre = self._normalize_text(genre)
        if genre == "qualquer":
            return [book for book in self.books if search_text in self._normalize_text(book['title']) or search_text in self._normalize_text(book['author'])]
        else:
            return [book for book in self.books if (search_text in self._normalize_text(book['title']) or search_text in self._normalize_text(book['author'])) and genre in self._normalize_text(book['genre'])]

    def rent_book(self, title, author, tenant_name, room_number):
        tenant_name = tenant_name.upper()
        if any(loan for book in self.books for loan in book['loans'] if loan['tenant_name'] == tenant_name and not loan['returned']):
            return "Você já tem um livro alugado. Devolva o livro atual antes de alugar um novo."

        for book in self.books:
            if self._normalize_text(book['title']) == self._normalize_text(title) and \
               self._normalize_text(book['author']) == self._normalize_text(author):
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
                    write_to_log(f"Rented book: {title} by {author} to {tenant_name} (Room/Role: {room_number})")
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
                    write_to_log(f"Returned book: {book['title']} by {tenant_name}")
                else:
                    updated_loans.append(loan)
            book['loans'] = updated_loans
        if book_returned:
            self.save_data()
            return "Empréstimo devolvido com sucesso."
        return "Nenhum empréstimo ativo encontrado para este locatário."

    def renew_loan(self, tenant_name):
        tenant_name = tenant_name.upper()
        for book in self.books:
            for loan in book['loans']:
                if loan['tenant_name'] == tenant_name and not loan['returned']:
                    new_return_date = (datetime.now() + timedelta(days=14)).strftime('%d/%m/%Y')
                    loan['return_date'] = new_return_date
                    loan['consecutive_loans'] = loan.get('consecutive_loans', 0) + 1
                    self.save_data()
                    write_to_log(f"Renewed loan for book: {book['title']} by {tenant_name} for another 14 days")
                    return f"Você está renovando o aluguel do livro {book['title']} por mais 14 dias, está certo disso?", \
                           book['title']
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
                        'genre': book['genre'],
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
                        'genre': book['genre'],
                        'tenant_name': loan['tenant_name'],
                        'room_number': loan['room_number'],
                        'return_date': loan['return_date'],
                        'consecutive_loans': loan.get('consecutive_loans', 0)
                    }
                    active_loans.append(loan_info)
        return active_loans

    def find_active_loans_by_name_or_title(self, search_query):
        search_query = self._normalize_text(search_query)
        active_loans = self.find_active_loans()
        result = [loan for loan in active_loans if
                  search_query in self._normalize_text(loan['tenant_name']) or
                  search_query in self._normalize_text(loan['title']) or
                  search_query in self._normalize_text(loan['room_number'])]
        return result

    def count_overdue_books(self):
        today = datetime.now().date()
        overdue_count = 0
        for book in self.books:
            for loan in book['loans']:
                return_date = datetime.strptime(loan['return_date'], '%d/%m/%Y').date()
                if return_date < today and not loan.get('returned', False):
                    overdue_count += 1
        return overdue_count

    @staticmethod
    def _normalize_text(text):
        return ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch)).lower()
