# Jaime-Kratz-Library-Software
In this project i volunteered myself to develop the library software of my school , Jaime Kratz, a Brazilian private school of Campinas, São Paulo. This is a simple library software that has a bunch of useful functions.

I write the whole code of the program in Python. I used the libraries: 

- tkinter
- datetime
- os
- json
- unicodedata

The software has two parts, the renter area and the administrator area.
In the renter area we have the functionalities:

- Search books
- Rent book - The user uses the search system to search a book, next the app shows a table with the search results and he click on the book that he want. After this he's asked his name, his room number or role in the school, and finally the book is rented.
- Return book - In this system, the user can only borrow one book at time, so he's asked just his name and then the book is returned.
- Back to main - The user is returned to the main screen of the software.

At the administrator area we have this functions:
(the user needs a password to access the admin. func.)

- Add book - The user is asked if he wants to add a new book or just add some units of a book that already exists at the database.
- Remove book - Work in the same way of the previous function.
- Search active loans - The user uses the search system to search for the title, renter's name or the room number or role.
- Show overdue books - The software work with a 14 day loan system, when the time has expired the loan data is shown in this function.
- Back to main

The software uses a JSON database system.
