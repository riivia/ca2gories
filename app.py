# To run:
# Set-ExecutionPolicy Unrestricted -Scope Process
# venv\Scripts\activate
# flask run --debug

# To stop:
# CTRL+C
# deactivate

from flask import Flask, redirect, render_template, request
from random import shuffle
from math import floor
from datetime import date, timedelta
from json import load
from obfuscator import obfuscate, unobfuscate

# Configure application
app = Flask(__name__)


# Day before the first puzzle
DAY_ZERO = date(2024, 7, 18)


@app.route("/")
def index():
    day = (date.today() - DAY_ZERO).days
    puzzle = get_puzzle(day)

    if puzzle is None:
        return render_error("No puzzle for today.")

    if "solved" not in request.args.keys():
        shuffle_tiles(puzzle["tiles"])
    
    today = format_date(puzzle["day"])

    return render_template("index.html", tiles=puzzle["tiles"], answers=puzzle["answers"], date=today)


@app.route("/archive")
def archive():
    if "day" not in request.args.keys():
        return render_template("archive.html", days=(date.today() - DAY_ZERO).days)

    # Check if day is a number
    try:
        day = int(request.args["day"])
    except ValueError:
        return render_error("Invalid day")

    # Check if day is not negative
    if day <= 0:
        return render_error("Date too early")
    
    # If day is today, go to index
    if day == (date.today() - DAY_ZERO).days:
        return redirect("/")

    # Check if day is in the future
    if day > (date.today() - DAY_ZERO).days:
        return render_error(f"Return at {format_date(day)}")
    
    puzzle = get_puzzle(day)

    if "solved" not in request.args.keys():
        shuffle_tiles(puzzle["tiles"])
    
    day_of = format_date(puzzle["day"])

    return render_template("index.html", tiles=puzzle["tiles"], answers=puzzle["answers"], date=day_of)


@app.route("/create")
def create():
    too_long = False
    MAX_WORD_LENGTH = 40
    MAX_ANSWER_LENGTH = 50

    # Load words that were submited
    NUMBER_OF_WORDS = 16
    words = [""] * NUMBER_OF_WORDS
    for i in range(NUMBER_OF_WORDS):
        field = f"word-{i}"
        if field in request.args.keys():
            word = request.args[field]
            if len(word) > MAX_WORD_LENGTH:
                word = word[:MAX_WORD_LENGTH]
                too_long = True
            words[i] = word
    
    # Load ansewers that were submited
    NUMBER_OF_ANSWERS = 5
    answers = [""] * NUMBER_OF_ANSWERS
    for i in range(NUMBER_OF_ANSWERS):
        field = f"answer-{i}"
        if field in request.args.keys():
            answer = request.args[field]
            if len(answer) > MAX_ANSWER_LENGTH:
                answer = answer[:MAX_ANSWER_LENGTH]
                too_long = True
            answers[i] = answer
    
    # Check if all the words and aswers were submited
    if "" not in words + answers and not too_long == True:
        data = {
            "answers": answers,
            "words": words
        }
        return redirect(f"/custom?data={obfuscate(data)}")

    return render_template("create.html", words=words, answers=answers)


@app.route("/custom")
def custom():
    # Check if there is data
    if "data" not in request.args.keys():
        return render_error("Invalid game")

    # Try decoding the data
    try:
        data = unobfuscate(request.args.get("data"))

        if data is None:
            return render_error("Invalid game")
    except Exception:
        return render_error("Invalid game")

    if "schema" in request.args.keys():
        return create_schema(data)

    tiles = create_tiles(data["words"])

    if "solved" not in request.args.keys():
        shuffle_tiles(tiles)

    return render_template("index.html", tiles=tiles, answers=data["answers"], date="Custom game")


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")


def get_puzzle(day):
    # Load the puzzles
    with open("static/puzzles.json", "r") as file:
        puzzles = load(file)

    if len(puzzles) < day:
        return None

    # Get the puzzle for today
    puzzle = puzzles[day - 1]

    words = []
    answers = [puzzle["special"]]
    for category in puzzle["categories"]:
        words += category["words"]
        answers.append(category["answer"])

    # Make a dictionary from the words
    tiles = create_tiles(words)
    
    return {
        "tiles": tiles,
        "answers": answers,
        "day": day
    }


def create_tiles(words):
    tiles = []
    for i in range(16):
        tiles.append(
            {
                "word": words[i],
                "category": floor(i / 4),
                "special": (i % 4 == 0),
            }
        )
    
    return tiles


def shuffle_tiles(tiles):
    while True:
        shuffle(tiles)
        if is_shuffled(tiles):
            return

def is_shuffled(tiles):
    for i in range(4):
        row = tiles[i * 4 : (i + 1) * 4]
        col = tiles[i::4]
        if not line_shuffled(row):
            return False
        if not line_shuffled(col):
            return False
    return True


def line_shuffled(line):
    count = {}

    # Count every category
    for tile in line:
        count[tile["category"]] = count.get(tile["category"], 0) + 1
        if tile["special"]:
            count[5] = count.get(5, 0) + 1

    # Check if any category appeared 3 or more times
    for value in count.values():
        if value >= 3:
            return False

    return True


def create_schema(data):
    schema = f'''{{<br />
        "special": '{data["answers"][0]}',<br />
        "categories": [<br />
            {{<br />
                "answer": '{data["answers"][1]}',<br />
                "words": {data["words"][:4]},<br />
            }},<br />
            {{<br />
                "answer": '{data["answers"][2]}',<br />
                "words": {data["words"][4:8]},<br />
            }},<br />
            {{<br />
                "answer": '{data["answers"][3]}',<br />
                "words": {data["words"][8:12]},<br />
            }},<br />
            {{<br />
                "answer": '{data["answers"][4]}',<br />
                "words": {data["words"][12:]},<br />
            }}<br />
        ]<br />
    }}'''
    schema = schema.replace("'", '"').replace("],", "]")
    return schema


def format_date(day):
    return (DAY_ZERO + timedelta(days=day)).strftime("%d %B %Y")


def render_error(message):
    return (render_template("error.html", message=message), 404)