from flask import Flask, render_template, session, request, make_response
from forms import NumberForm, HurdleForm, WhurdleForm
from flask_session import Session
import random
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-a-secret-key_only-i-know"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Problem 1
@app.route("/guess", methods=["GET","POST"])
def guess():
    form = NumberForm()
    message = ""
    if "secret_number" not in session:
        session["secret_number"] = random.randint(0, 100)
    secret_num = session["secret_number"]
    if form.validate_on_submit():
        number = form.number.data
        if number == secret_num:
            message = "Congrats! You guessed the number!"
        elif number < secret_num:
            message = "The number is bigger"
        else:
            message = "The number is smaller"
    return render_template("guess.html", form=form, message=message)



# CHALLENGE (1st PART - LIKE WORDLE BUT ONE WORD PER SESSION)
@app.route("/hurdle", methods=["GET","POST"])
def hurdle():
    form = HurdleForm()
    message = ""
    available_letters = ""

    # Call function to get list of words from textfile
    word_list = get_list_words("five_letter_words.txt")
    # Choose a random word from word_list and save it on session file. Initialize a key/value pair for tries ("tries":0), a dictionary for all the user guesses and a victory "flag". Added a list of letters that haven't been used by the user yet for easier gameplay.
    if "secret_word" not in session:
        session["secret_word"] = random.choice(word_list)
        session["tries"] = 0
        session["guess_history"] = {}
        session["victory"] = False
        session["available_letters"] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    # Assign to variable secret_word the word stored in session for this user
    secret_word = session["secret_word"]
    tries_left = 6 - session["tries"]

    if form.validate_on_submit():
        # Get user's guess and transform to lowercase
        guess = form.guess.data.lower()
        # Check if user has guessed the word already
        if session["victory"] == True:
            message = "Hey! You already played and guessed the right word!"
        # Check if the guess word has less than 5 letters
        elif len(guess) != 5:
            form.guess.errors.append("Enter a 5 letter word please")
        # Check if user has tried 6 times already.
        elif session["tries"] == 6:
            message = "You ran out of tries. The correct word was:"
        # Check if the user has guessed the word.
        elif guess == secret_word:
            message = "Congratulations. You guessed it!"
            session["victory"] = True
        else:   # Wrong word
            #Check if the word doesn't appear in the list of words.
            if guess not in word_list:
                message = "Word not in word list"
            else:  # Word appears in our list
                scores = calculate_score(guess, secret_word, session["available_letters"])
                exact_position = scores[0]
                wrong_position = scores[1]
                session["available_letters"] = scores[2]
                # Value for Key "tries" in session increased by 1
                session["tries"] = session["tries"] + 1
                # Save into the guess_history dictionary (in session) the guess result of the attempt in a new dictionary. I used the tries value in session to create the key of this new dict:
                session["guess_history"][str(session["tries"])] = {}
                session["guess_history"][str(session["tries"])]["1"] = guess.upper()
                session["guess_history"][str(session["tries"])]["2"] = exact_position
                session["guess_history"][str(session["tries"])]["3"] = wrong_position

                tries_left -= 1
                if tries_left == 0:
                    message = "You ran out of tries. The correct word was:"

        available_letters = session["available_letters"]
        available_letters = [letter.upper() for letter in available_letters]

    return render_template("hurdle.html", title="HURDLE!", form=form, message=message, tries_left=tries_left, guess_history=session["guess_history"], victory=session["victory"], secret_word=session["secret_word"], available_letters=available_letters)


# Function definition to get a list of words from a text file (where each word is in a new line)
def get_list_words(filename):
    word_list = []
    fin = open(filename, "r")
    for row in fin:
        word_list.append(row.strip())
    fin.close()
    return word_list


# Function definition to calculate the scores of 2 given words.
def calculate_score(user_word, secret_word, available_letters):
    # Initialise variables
    exact_position = []   # List of letters in the same position in both the user's word and secret word
    wrong_position = []   # List of letters in the user's word that appear in the secret word but are in wrong position
    used_letters = ""     # String that will be constructed with the letters that appear in either exact_position or wrong_position


    i = 0
    # Iterate through every letter in user's word to validate with the secret word.
    for letter in user_word:

        if letter in available_letters:
            available_letters.remove(letter)

        if letter in secret_word:
            # Count how many times the letter appears in the secret word and the used_letters.
            count_UsedLetters = used_letters.count(letter)
            count_SecretWord = secret_word.count(letter)

            # Save the index of every time "letter" appears in secret word / user's word:
            indices_secretW = [i for i, x in enumerate(secret_word) if x == letter]     # Wanted to validate the position of each letter, needed to save all indices of the letter in the word, learned enumerate() here: https://stackoverflow.com/questions/6294179/how-to-find-all-occurrences-of-an-element-in-a-list
            indices_userW = [i for i, x in enumerate(user_word) if x == letter]
            
            if letter == secret_word[i]:  #correct letter and position
                exact_position.append(letter)
                used_letters = used_letters + letter

            else:   # correct letter, wrong position
                # Check how many times this letter in the user's word is in the right position in the secret word
                correct_counter = 0
                for item in indices_userW:
                    for Item in indices_secretW:
                        if item == Item:
                            correct_counter += 1
                if correct_counter != count_SecretWord and count_UsedLetters < count_SecretWord:
                    wrong_position.append(letter)
                    exact_position.append("_")
                    used_letters = used_letters + letter
                else:   # letter already appears in exact_position+wrong_position lists the same amount of times as it appears in secret_word
                    exact_position.append("_")

        else: #letter not in secret_word
            exact_position.append("_")

        i += 1
    
    # Transform both lists of matching letters into strings (easier to be displayed later in the website when passing them to the Jinja template). Uppercase them.
    exact_position = " ".join(exact_position).upper()
    wrong_position = ", ".join(wrong_position).upper()

    # If there are no letters in the wrong position, assign a dash to it.
    if wrong_position == "":
        wrong_position = "-"

    return exact_position, wrong_position, available_letters


# CHALLENGE (2nd part - LIKE WORDLE (ONE WORD PER DAY))
#Route same as "/hurdle", but with the session key names changed and calling for a function to get the daily secret word
@app.route("/whurdle", methods=["GET","POST"])
def whurdle():
    form = WhurdleForm()
    message = ""
    available_letters = ""

    # Call function to get list of words from textfile
    word_list = get_list_words("five_letter_words.txt")
    # Calculate the daily  it on session file. Initialize a key/value pair for tries ("tries":0), a dictionary for all the user guesses and a victory "flag".
    if "secret_word_daily" not in session:
        session["secret_word_daily"] = today_secret_word(word_list)   # Get todays' secret word out of the word list
        session["tries_daily"] = 0
        session["guess_history_daily"] = {}
        session["victory_daily"] = False
        session["available_letters_daily"] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    secret_word = session["secret_word_daily"]
    tries_left = 6 - session["tries_daily"]

    if form.validate_on_submit():
        # Transform to lowercase
        guess = form.guess.data.lower()
        # Check if user has guessed the word already
        if session["victory_daily"] == True:
            message = "Hey! You already played and guessed the right word! Come back tomorrow ;)"
        # Check if the guess word has less than 5 letters
        elif len(guess) != 5:
            form.guess.errors.append("Enter a 5 letter word please")
        # Check if user has tried 6 times already.
        elif session["tries_daily"] == 6:
            message = "You ran out of tries. The correct word was:"
        # Check if the user has guessed the word.
        elif guess == secret_word:
            message = "Congratulations. You guessed it!"
            session["victory_daily"] = True
        else:   # Wrong word
            #Check if the word doesn't appear in the list of words.
            if guess not in word_list:
                message = "Word not in word list"
            else:  # Word appears in our list
                scores = calculate_score(guess, secret_word, session["available_letters_daily"])
                exact_position = scores[0]
                wrong_position = scores[1]
                session["available_letters_daily"] = scores[2]
                # Value for Key "tries" in session increased by 1
                session["tries_daily"] = session["tries_daily"] + 1
                # Save into the guess_history dictionary (in session) the guess result of the attempt in a new dictionary. I used the tries value in session to create the key of this new dict:
                session["guess_history_daily"][str(session["tries_daily"])] = {}
                session["guess_history_daily"][str(session["tries_daily"])]["1"] = guess.upper()
                session["guess_history_daily"][str(session["tries_daily"])]["2"] = exact_position
                session["guess_history_daily"][str(session["tries_daily"])]["3"] = wrong_position

                tries_left -= 1
                if tries_left == 0:
                    message = "You ran out of tries. The correct word was:"

        available_letters = session["available_letters_daily"]
        available_letters = [letter.upper() for letter in available_letters]
        
    return render_template("whurdle.html", title="WHURDLE!", form=form, message=message, tries_left=tries_left, guess_history=session["guess_history_daily"], victory=session["victory_daily"], secret_word=session["secret_word_daily"], available_letters=available_letters)


def today_secret_word(list_of_words):
    seed = date.today()      # Seed understanding: https://pynative.com/python-random-seed/
    random.seed(str(seed))
    secret_word = random.choice(list_of_words)
    return secret_word

# def today_secret_word(list_of_words):
#     response = make_response()
#     # Chose random word according to today's date:
#     seed = date.today()      # Seed understanding: https://pynative.com/python-random-seed/
#     random.seed(str(seed))
#     secret_word = random.choice(list_of_words)
#     # Create cookie with the random word and set expiry date to midnight.
#     tomorrow = datetime.now() + timedelta(1)    # https://www.geeksforgeeks.org/python-find-yesterdays-todays-and-tomorrows-date/
#     today_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
#     response.set_cookie("secret_word_daily", secret_word, expires=today_midnight)
#     return response