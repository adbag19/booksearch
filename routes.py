#!/usr/bin/env python3
from flask import Flask, render_template, request, url_for, redirect, jsonify
from Templates import BookTemplate, setAttributes, AuthorTemplate
from getData import goodreads_get_book_data, goodreads_get_author_data

# Init Flask
app = Flask(__name__)

@app.route('/')
def form():
    return render_template("form.html")
@app.route('/index', methods=['GET','POST'])
def index():
    if request.method=='POST':
        #Example Book
        bookTitle = request.form['booktitle']
        bookAuthor = request.form['bookauthor']

        # this calls the API and related helper functions!
        goodreads_get_book_data(bookTitle, bookAuthor)

        # create object/instance of the Book class
        book = BookTemplate()

        #  Assign the data dictionary as attributes of the object as shown
        setAttributes (book, goodreads_get_book_data(bookTitle, bookAuthor))

        # Now, you can access the attributes of the book directly by referring to the object:
        print (book.title)
        
        # You can also access similar books by access that data dictionary.
        # Remember, it's an array of dictionaries though, so you have to refer to a specific item, or loop through all:
        if book.title==None:
            print('No similar books')
            return render_template('error.html', book=book)
        else:
            print (book.similar_books[0]['title'])

        # To get author info, you must collect author info.  It's a slightly different API in Goodreads
         
         # This will call the API and hepler functions from getData.py.  
         # Here, we are also passing along the same author and title variables from above (you will get these from your wtf input forms)  

        # First, we will create a second object to store author data.
        # Why do we need this?  Because the data being returned pertains directly to the author, not the book 
            authorTemplate = AuthorTemplate()
            
            # We call setAttributes again to assign the dictionary items to the object
            # Like the book object, we can now call these by referencing the object
            setAttributes(authorTemplate, goodreads_get_author_data(bookAuthor, bookTitle))

            # Now we associate the author object with the book object
            book.authorProfile = authorTemplate

            # Now, we can access author data directly.  
            # Where are we getting this?  From parse_response_author in the getData file!
            # Plese see the URL created in getData.py for all the attributes
            # Here is JSON data for author's published books:
            #print (book.authorProfile.books)

            # Here is the dictionary version:
            print (book.authorProfile.books_dict)

            # Now, to pass this information on to the webpage, we can simply pass the "book" object we created above along as a variable.  Now we can call this object and its attributes using jinja (see index.html provided)

            return render_template('index.html', book=book)
    else:
        return render_template('form.html')

if __name__ == "__main__":
    app.run(debug=True)
