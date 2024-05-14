Jaime-Kratz Library Project
	In this project, I volunteered myself to develop the library software of my school, Jaime Kratz, a Brazilian private school in Campinas, São Paulo. This is a simple library software that has a bunch of useful functions.

	I wrote the whole code of the program in Python. I used the libraries: 
		
		- Tkinter
		- DateTime
		- os
		- JSON
		- Unicode data
		
		The software has two parts, the renter area and the administrator area.
		In the renter area, we have the functionalities:
		
		- Search books
		- Rent book - The user uses the search system to search a book, next the app shows a table with the search results and he clicks on the book that he wants. After this, he's asked for his name, his room number, or role in the school, and finally, the book is rented.
  		- Renew loan - The user inserts his name and the loan is renewed.
		- Return book - In this system, the user can only borrow one book at a time, so he's asked just his name and then the book is returned.
		- Back to main - The user is returned to the main screen of the software.
		
		In the administrator area, we have these functions:
		(the user needs a password to access the admin. func.)
		
		- Add book - The user is asked if he wants to add a new book or just add some units of a book that already exists in the database.
		- Remove book - Work in the same way as the previous function.
		- Search active loans - The user uses the search system to search for the title, renter's name, or room number or role.
		- Show overdue books - The software works with a 14-day loan system, when the time has expired the loan data is shown in this function.
		- Back to main
		
		The software uses a JSON database system.
