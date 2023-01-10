import sqlite3
from datetime import datetime
import os

# Create the table if it doesn't exist
def create_table():
    """Create a table with the following columns:
    
    word: (VARCHAR(50)), the unique word to be remembered 
    definition: (VARCHAR(400)), the definition of the word 
    EF: INT, the Easyness Factor that is adjusted by user selected difficulty of recall:
        {'Again': -0.2, 'Hard': -0.15, 'Good': 0, 'Easy': +0.15} 
        Has a floor of 1.3
    CI: INT, Current Interval that is adjusted by the following formula each time EF changes:
        CI_new = CI_old * EF
    isGraduate: Bool, indicates whether word has graduated or not 
    time: INT, concatenation of current datetime removing all punctuation:
         %Y%m%d%H%M%S
    SI: INT, Student Interval, the interval lengths
    
    """
    path = './wordbank.db'
    if not os.path.exists(path): 
        # create our database if it doesn't exist
        # create a table for words
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists words(
        word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT, SI INT, UNIQUE(word))
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
def fetch_word(word):
    """Returns a list of tuples containing the word and all it's attributes"""

    conn, c = create_connection()
    c.execute("SELECT * FROM words WHERE word = ?", (word,))
    word_row = c.fetchall()
    conn.close()
    return word_row[0]

# Delete a word from the database
def delete_word(word):
    conn, c = create_connection()
    c.execute("DELETE FROM words WHERE word = ?", (word,))
    conn.commit()
    conn.close()
    
# Add a new word to the database
def add_word(word, definition, EF=2.5, CI=1, isGraduate=False, time=int(datetime.now().strftime("%Y%m%d%H%M%S")), SI=1):
    conn, c = create_connection()
    c.execute("INSERT INTO words VALUES(?, ?, ?, ?, ?, ?, ?)", (word, definition, EF, CI, isGraduate, time, SI))
    print(f"Added word to wordbank: word = \"{word}\", EF = {EF}, CI = {CI}, isGraduate = {isGraduate}, time = {time}, SI = {SI}")
    conn.commit()
    conn.close()


# Update a word in the database
def update_word(word, definition, EF, CI, isGraduate, time, SI):
    conn, c = create_connection()
    c.execute("UPDATE words SET definition = ?, EF = ?, CI = ?, isGraduate = ?, time = ?, SI = ? WHERE word = ?", (definition, EF, CI, isGraduate, time, SI, word))
    conn.commit()
    conn.close()
    print(f"Updated word : word = \"{word}\", EF = {EF}, CI = {CI}, isGraduate = {isGraduate}, time = {time}, SI = {SI}, \n definition = {definition}")

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
    word_row = c.fetchall()
    word_row = word_row[0]
    word = word_row[0]
    definition = word_row[1] 
    ef = word_row[2]
    ci = word_row[3]
    isGraduate = word_row[4]
    time = word_row[5]
    si = word_row[6]

    print(f"Fetched word from wordbank: word = \"{word}\", EF = {ef}, CI = {ci}, isGraduate = {isGraduate}, time = {time}, SI = {si}, \n definition = {definition}")
    return word_row
