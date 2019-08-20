import requests
import xmltodict
import itertools
from datetime import datetime

key_goodreads = 'SEX1X3AqNPEW9w5U8AfUA'
base_url_goodreads = 'https://www.goodreads.com/search.xml?key=' + key_goodreads 


# This function is the primary for accessing the data. 
# It accepts a title and author.  It can be changed to accept other things, like ISBN#
# As you can see, a lot of work must be done in order to use the response, please see the helper functions below
def goodreads_get_book_data(title, author):
    url = build_url_book(title, author)
    print (url)

    response = requests.get(url)
    
    if response.status_code == 200:
        # This return json.  We want to enter at the 
        r = xmltodict.parse(response.text)['GoodreadsResponse']['book']

        try:
            similar_books = parse_similar_books(r['similar_books']['book'])
        except KeyError:
            similar_books = None

        goodreads_data_dictionary = {
            'isbn': r['isbn'],
            'isbn13' : r['isbn13'],
            'title': r['title'],
            'year': r['publication_year'],
            'original_publication_year': r['work']['original_publication_year']['#text'],
            'publisher': r['publisher'],
            'language': r['language_code'],
            'description': r['description'],
            'pages': r['num_pages'],
            'author': parse_authors(r['authors']['author']),
            'shelves': parse_shelves(r['popular_shelves']['shelf']),
            'similar_books': similar_books,
            'goodreads_author_img': parse_authors_image(r['authors']['author']),
            # THINKME: If we store authors id, need to handle multiple authors case
            # 'goodreads_author_id': r['authors']['author']['id'],
            'goodreads_url': r['url'],
            'goodreads_book_img': get_image_url(r['image_url']),
            'goodreads_rating': r['average_rating'],
            'not_found': False
        }

        return goodreads_data_dictionary
    else:
        return {'not_found': True}

######## HELPER FUNCTIONS #########

# Bunch of functions to help get the data and parse.  
# These would ideally be in a separate file, but including here for simplicity!!!

# We need this for searches with spaces, adds %20 instead!
def encode_white_spaces(string):
    return string.replace(' ', '%20')

def parse_authors(authors):
    if type(authors) is list:
        return parse_authors_from_list(authors)
    return authors['name']

def parse_shelves(shelves):
    shelves_and_counts = dict()
    for shelf in shelves:
        name = normalize(shelf['@name'])
        if name not in ['to read', 'currently reading']:  # arbitrarily exclude some shelves
            shelves_and_counts[name] = shelf['@count']
        elif name in shelves_and_counts:
            shelves_and_counts[name] = shelves_and_counts[name] + shelf['@count']
    return transform_shelves_dict_to_list(shelves_and_counts)

def request(url):
    return requests.get(url)

def request_author_id(title, author):
    response = request_book(author, title)
    if response.status_code == 200:
        return parse_author_id(response, author)
    else:
        return None

def request_book(author, title):
    url = build_url_book(title, author)
    return request(url)

def parse_similar_books(similar_books):
    books = []
    for book in similar_books:
        books.append({
            'title': book['title'],
            'isbn': book['isbn'],
            'goodreads_rating': book['average_rating'],
            'goodreads_book_img': get_image_url(book['image_url']),
            'pages': book['num_pages'],
            'goodreads_url': book['link'],
            'year': book['publication_year'],
            'author': book['authors']['author']['name'],  # TODO: Handle multiple authors
        })
    return books

def transform_shelves_dict_to_list(shelves_and_counts):
    shelves_list = []
    for k, v in shelves_and_counts.items():
        shelves_list.append({'name': k, 'count': v})
    return shelves_list

def parse_authors_image(authors):
    if type(authors) is list:
        return parse_authors_image_from_list(authors)
    return get_image_url(authors['image_url']['#text'])

def get_image_url(url):
    search_str = '/nophoto/'
    return None if search_str in url else url

def normalize(name):
    return name.lower().replace('-', ' ').replace('_', ' ')

def similar_books(r):
    #print (r['similar_books']['book'])
    
    try:
        similar_books = parse_similar_books(r['similar_books']['book'])
    except KeyError:
        similar_books = None
    return similar_books

    def request_author_id(title, author):
        response = request_book(author, title)
        if response.status_code == 200:
            return parse_author_id(response, author)
        else:
            return None

def parse_author_id(response, name):
    author = xmltodict.parse(response.text)['GoodreadsResponse']['book']['authors']['author']
    if type(author) is not list:
        return author['id']
    for a in author:
        # THINKME: Name might have a slightly different format so this check is not perfect
        if a['name'].lower() == name.lower():
            return a['id']

def build_url_author(id):
    return 'https://www.goodreads.com/author/show/%s?format=xml&key=%s' % (id, key_goodreads)
    
def build_url_book(title, author):
    a = encode_white_spaces(author)
    t = encode_white_spaces(title)
    url = 'https://www.goodreads.com/book/title.xml?author=%s&key=%s&title=%s' % (a, key_goodreads, t)
    #print (url)    
    return url

def goodreads_get_author_data(name, a_book):
    author_id = request_author_id(a_book, name)
    if author_id is None:
        return {'not_found': True}

    url = build_url_author(author_id)
    print (url)
    response = request(url)
    if response.status_code == 200:
        return parse_response_author(response)
    else:
        return {'not_found': True}
    
def parse_response_author(response):
    author = xmltodict.parse(response.text)['GoodreadsResponse']['author']

    # Fixing birthdate format
    

    return {
        'name': author['name'],
        'about': author['about'],
        'influences': parse_influences_html(author['influences']),
        'hometown': author['hometown'],
        'goodreads_link' : author['link'],
        'goodreads_img_url': get_image_url(author['large_image_url']),
        'books_dict' : parse_authors_books_dict(author['books']['book']),
        'books' : parse_authors_books(author['books']['book'])
    }

def parse_authors_books_dict(books_dict):
    b = []
    for book in books_dict:

        # We'd ideally get the origisetAttributesnal publication date of the book.  Unfortuntely this only returns
        # the most recent edition. To get the original date, we'd need to make a separate call to goodreads by isbn and get the original_publication_date

        t = encode_white_spaces(book['title_without_series'])

        if book['published']:
            b.append({
                'content': '<a href="' + t + '">' + book['title'] + '</a>',
                'start': book['published'],
            })

    return b

def parse_authors_books(books):
    b = []
    for book in books:
        b.append({
            'isbn' : book['isbn'],
            'title' : book['title'],
            'goodreads_image_url' : get_image_url(book['image_url']),
            'goodreads_link' : book['link'],
            'pages' : book['num_pages'],
            'publisher' : book['publisher'],
            'publication_day' : book['publication_day'],
            'publication_year' : book['publication_year'],
            'publication_month' : book['publication_month'],
            'goodreads_rating' : book['average_rating'],
            'goodreads_raters' : book['ratings_count'],
            'description' : book['description'],
            'authors' : book['authors'] # TODO: Get authors in a nice format - mostly to know if there are other authors
        })
    return b

def parse_influences_html(influences_html):
    if (influences_html is None):
        return
    influences = []
    for value in influences_html.split('</a>'):
        v = value.split('>')
        if len(v) > 1:
            influences.append(v[1])
    return influences

def parse_authors_from_list(authors):
    author_string = authors[0]['name']
    last = len(authors) - 1
    for author in itertools.islice(authors, 1, last):
        author_string += ", " + author['name']
    if last >= 0:
        author_string += " and " + authors[last]['name']
    return author_string

def parse_authors_image_from_list(authors):
    urls = []
    for author in authors:
        urls.append(get_image_url(author['image_url']['#text']))
    return urls