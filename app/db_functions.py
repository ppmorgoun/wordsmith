import sqlite3
from datetime import datetime
import os

# Create the table if it doesn't exist
def create_table():
    path = './wordbank.db'
    if not os.path.exists(path): 
        # create our database if it doesn't exist
        # create a table for words
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists words(
        word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT, UNIQUE(word))
        """)
        conn.commit()
        conn.close()
        # add "Wordsmith" to the database
        add_word('Wordsmith', 'A skilled user of words')


# Create a connection and a cursor to the database
def create_connection():
    conn = sqlite3.connect('wordbank.db')
    c = conn.cursor()
    return conn, c

# fetch word and definition from database
def fetch_word():
    pass

# Delete a word from the database
def delete_word(word):
    conn, c = create_connection()
    c.execute("DELETE FROM words WHERE word = ?", (word,))
    conn.commit()
    conn.close()
    
# Add a new word to the database
def add_word(word, definition, EF=2.5, CI=1, isGraduate=False, time=int(datetime.now().strftime("%Y%m%d%H%M%S"))):
    conn, c = create_connection()
    c.execute("INSERT INTO words VALUES(?, ?, ?, ?, ?, ?)", (word, definition, EF, CI, isGraduate, time))
    conn.commit()
    conn.close()


# Update a word in the database
def update_word(word, definition, EF, CI, isGraduate, time):
    conn, c = create_connection()
    c.execute("UPDATE words SET definition = ?, EF = ?, CI = ?, isGraduate = ?, time = ? WHERE word = ?", (definition, EF, CI, isGraduate, time, word))
    conn.commit()
    conn.close()

# Return a list of all the words from the database
def fetch_all_words():
    conn, c = create_connection()
    c.execute("SELECT word FROM words")
    words = c.fetchall() # this is a list of tuples
    conn.close()
    return words

# Return a list of all the words and their definitions from the database
def fetch_all_words_with_defs():
    conn, c = create_connection()
    c.execute("SELECT word, definition FROM words")
    words_with_defs = c.fetchall() # this is a list of tuples
    conn.close()
    return words_with_defs

# Fetch next word to be reviewed

def fetch_next_word():
    """Returns the word row of the word with the lowest CI and time"""
    conn, c = create_connection()
    c.execute("SELECT * FROM words WHERE CI = (SELECT MIN(CI) FROM words)" \
        " AND time = (SELECT MIN(time) FROM (SELECT * FROM words WHERE CI = (SELECT MIN(CI) FROM words)))")
    word_row= c.fetchall()
    conn.close()
    return word_row
