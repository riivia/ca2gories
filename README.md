# Ca2gories

### [Video Demo](https://youtu.be/fCtMsJuYPE8)

## About:

Ca2gories is a daily puzzle game.

It takes inspiration from games like:
- [New York Times Connections](https://www.nytimes.com/games/connections)
- [Clevergoat Categories](https://categories.clevergoat.com/)
- [Cine2Nerdle](https://www.cinenerdle2.app/)

The board is made out of 16 tiles arranged in a 4x4 grid. Every tile has a word or a phrase on it. There are 5 hidden groups consisting of 4 tiles each. If the player manages to put 4 tiles belonging to the same category in a row or a column, the theme of that category is revealed. If the are 3 tiles belonging to the same category in a row or a column, they turn yellow as a hint to the player. To win, the player has to correctly arrange all the tiles in their respective categories. To discourage the players from randomly shuffling the tiles, there is a limit of 15 swaps. Because there are 5 categories, one tile from each of the 4 base categories also belongs to the 5th special category. This means that on a solved board each of the base categories is arranged in a row, then the special category is in a column (and vice versa).

## [game.js](static/game.js)
Manages all of the game's logic.

The drag and drop mechanics use the _draggable_ property in HTML.

Under each tile there is a **slot**. Each slot has a _data-x_ and _data-y_ property to indicate it's coordinates on the game grid. A slot reacts to the `dragover` and dragend events which allows it to detect if there are under the mouse while it is dragging a tile. If so, the slot gains the closest class.

A **tile** reacts to the dragstart and dragend to detect when it is dragged. It gains the dragging class.

#### dragend
Is triggered when a tile is dropped. It checks if there is a slot with class closest. If there is one it then checks if it isn't the slot where the tile currently is. If it isn't it swaps itself with the tile in that slot. Finally it [updates the board](#updatetiles) and [counts the move](#countmoves).
> Note that the tile also checks if there are any moves left, because even when the `draggable` property is set to `false`, you can sometimes still dragg the tile when clicking on a it's corner. This part makes sure that the tile will not move in that case.
```
tile.addEventListener('dragend', () => {
    tile.classList.remove('dragging')
    if (movesMade == maxMoves) {
        return
    }

    const closest = document.querySelector('.closest')
    if (closest) {
        closest.classList.remove('closest')
        const parent = tile.parentNode
        if (closest != parent) {
            parent.appendChild(closest.children[0])
            closest.appendChild(tile)
            updateTiles()
            countMove()
        }
    }
})
```

After each move, the game updates it's state. This depends on three main functions: [updateTiles()](#updatetiles), [updateCategory()](#updatecategory) and [update_line()](#updateline).

#### updateTiles()
The function loops through every basic category. First it resets the color of all the tiles by removing category, special and almost classes:
```
tiles.forEach( tile => {
    tile.classList.remove('category-' + tile.dataset.category)
    tile.classList.remove('special')
    tile.classList.remove('almost')
})
```

Then it runs the updateCategory() function on it.

#### updateCategory()
Loops through every row and column by getting the slots with corresponding _dataset.x_ or _dataset.y_ and selects each tile from current category in said row/column:
```
function updateCategory(tiles, special=false)
{
    for (let i = 0; i < 4; i++) {
        let row = [...tiles].filter(tile => tile.parentNode.dataset.x === i.toString())
        let col = [...tiles].filter(tile => tile.parentNode.dataset.y === i.toString())
        if (updateLine(row, special) || updateLine(col, special)) {
            return true
        }
    }
}
return false
```

#### updateLine()
Is run on each set of tiles in the same row/column. Remember that now the line array consists only of tiles from the same category that are in the same row/column. This means that now comparing the length of the line lets us know if the tile should change color. If there are 4 tiles in a line, the tile should change color to one corresponding to it's category. If there are 3 tiles, it should change to yellow, to hint the player that they are close.

> Note that the 'almost' class should always display on top, because it is possible for a tile to be guessed for one category and almost guessed for another.

```
function updateLine(line, special=false)
{
    // If there are 4 tiles in a line, mark solved
    if (line.length == 4) {
        line.forEach( tile => {
            if (special == true) {
                tile.classList.add('special')
            } else {
                tile.classList.add('category-' + tile.dataset.category)
            }
        })
        return true
    // If there are 3 tiles in a line, mark hint
    } else if (line.length == 3) {
        line.forEach( tile => {
            tile.classList.add('almost')
        })
    }
    return false
}
```
The function returns _true_ if a category is guessed, so that the answer to said category can be displayed. It both removes and adds a class, because _not-guessed_ hides the answer and _guessed_ animates it:
```
answers[c].classList.remove('not-guessed')
answers[c].classList.add('guessed')
```

Then the [updateCategory()](#updatecategory) function is called once more for the special category. It is done this way, because belonging to the special category is indicated by separate data data-special: true.
> Note that the special category can't be signified by just setting the data-category: 5 because every tile in the special category also belongs to one of four basic categories.

The [updateTiles()](#updatetiles) function counts how many categories are correct in the current check by counting up the _solved_ variable. So if in the end _solved == 5_, it knows the puzzle is solved and calls the [animateVictory()](#animatevictory) function.

#### countMoves()
Is triggered in  after every tile swap. It is not triggered if a tile is simply picked up and placed down without swaping.If there is just one move remaining, a popup is showed to let the player know about it.

If the player doesn't have any more moves, all the tiles are set to not be draggable anymore.
> The popup was made based on [this W3Schools tutorial](https://www.w3schools.com/howto/howto_js_popup.asp).
```
// Count the moves
function countMove(reset=false) {
    if (reset) {
        movesMade = 0
    } else {
        movesMade = movesMade + 1
    }

    if (maxMoves - movesMade == 1) {
        popup.classList.toggle("show")
    } else if (movesMade == maxMoves) {
        tiles.forEach(tile => {
            tile.setAttribute('draggable', false)
        })
    }
    document.getElementById('counter').innerText = 'Moves made: ' + movesMade + '/' + maxMoves
}
```

#### animateVictory()
Creates and array of all tiles. It loops through them and adds event listener for animationend to each. Finally it waits 500ms and triggers the _animateTile()_ function.
```
function animateVictory() {
    let remaining = [...document.querySelectorAll('.tile')]
    remaining.forEach( tile => {
        tile.addEventListener('animationend', () => animateTile(remaining), { once: true })
    })
    setTimeout(animateTile, 500, remaining)
}
```

The _animateTile()_ function removes the first tile in the _remaining_ list and plays it's animation by adding the solved class. Because each tile has an event listener, that calls this function at the end of it's animation, every tile will animate one after another. If all tiles were already animated, the function animates all the tiles again, this time all at once. The line `void tile.offsetWidth` makes resets the animation, so it plays correctly when re-adding the solved class.
> Note that the event listener is set to trigger only once `{ once: true }`. Otherwise when the animation would never stop.
```
function animateTile(remaining) {
    if (remaining.length == 0){
        document.querySelectorAll('.tile').forEach( tile => {
            tile.classList.remove('solved')
            void tile.offsetWidth;
            tile.classList.add('solved')
        })
    } else {
        remaining.shift().classList.add('solved')
    }
}
```

## [Puzzle data](static/puzzles.json) **SPOILERS IN THE FILE!**

All puzzles are stored in a list of dictionaries in such form:
> With each first word in a category also belongs to the special category.
```
{
        "special": "CS50 subjects",
        "categories": [
            {
                "answer": "Letters of the alphabet",
                "words": ["C", "A", "B", "D"]
            },
            {
                "answer": "Snakes",
                "words": ["Python", "Cobra", "Boa", "Viper"]
            },
            {
                "answer": "Minor injuries",
                "words": ["Scratch", "Bruise", "Scrape", "Scuff"]
            },
            {
                "answer": "Containers",
                "words": ["Flask", "Vase", "Bottle", "Jar"]
            }
        ]
    }
```

## [app.py](app.py)
Is a web application written in Python using Flask.

### Functions
Day is an integer counting how many days passed since **DAY_ZERO** which is the day before the first puzzle.

#### get_puzzle()
Loads the puzzle from the .json file and arranges it into a dictionary.
```
def get_puzzle(day):
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
```

#### create_tiles()
Returns an array of dictionaries with the data for each tile. It is important to note which category a tile belongs to before shuffling them.
```
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
```

#### shuffle_tiles()
Randomizes the order of the tiles until there are no 3 or 4 tiles from the same category in any row or column. It makes sure that there is no information available before making a move. The logic is analogous to the [updateTiles()](#updatetiles) in [game.js](#gamejs).
```
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
```

### Routes

#### Main
Loads the puzzle for the current day. Each route that loads a puzzle, supports the _solved_ argument. It ommits the shuffling of the tiles, and was mainly used for debugging.
```
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
```

#### Archive
Let's the user choose one of the previous puzzles. It runs a series of checks to make sure that the given day is valid. If the day would show today's puzzle, it redirects to the main route. If the day would be in the future, it displays a message to return at a given date.
```
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
```

#### Create
Let's the user make their own puzzle. If the form is submitted without filling all the fields, the page is reloaded keepeing all the previously filled fields. Otherwise it redirects to the [/custom](#custom) route.
> Note that before sending the data to [/custom](#custom) it is first obfuscated. It is not done for security reasons, but to make sure that the player doesn't accidentally spoil the answer by simply looking at the arguments in the link.

THe form checks if the provided input is not too long. I don't bother displaying an error message, becuase to send longer inputs the user needs to edit the html. Also the limits are very big (40 characters for a tile and 50 characters for an answer).

> The code for obfuscating and unobfuscating data was created with the help of [ChatGPT](https://chatgpt.com/) and is located in [obfuscator.py](obfuscator.py)
```
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
```

### Custom
Takes the data created in [/create](#create). It unobfuscates it into a dictionary and loads a game from it. It makes sure that the passed data is valid and renders an error otherwise.
> Adding the `schema` argument, returns the data in a string formatted like a dictionary. It allows me to use the create tool to make new entries for [Puzzle data](#puzzle-data-spoilers-in-the-file)
```
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
```

### Instructions
Shows instructions on how to play the game.
```
@app.route("/instructions")
def instructions():
    return render_template("instructions.html")
```

## Templates
### [Layout](templates/layout.html)
Is the basis of all other pages. It is pretty basic. It contains the navbar, the footer and placeholders for the title and body.
```
<header>
    <div class="navbar">
        <a class="site-name" href="/">Ca2gories</a>
        <div class="navbar-buttons">
            <a href="/instructions">How to Play</a>
            <a href="/archive">Archive</a>
            <a href="/create">Create</a>
        </div>
    </div>
</header>
```
```
<footer>
    Game by Michał Niemier
</footer>
```

### [Index](templates/index.html)
Makes the game board by creating a 4x4 table. A slot is placed in each cell and has _data-x_ and _data-y_ properties to mark it's coordinates on the grid. A tile is placed in each slot. A tile is _draggable_, has _data-category-#_ signifying to which base category it belongs to and _data-special_ set to True if it belongs to the special category.
```
<table>
    {% for y in range (4) %}
        <tr>
            {% for x in range(4) %}
                {% set tile = tiles[y * 4 + x] %}
                <td>
                    <!-- Create a slot -->
                    <div class="slot" data-x="{{ x }}" data-y="{{ y }}">
                        <!-- Create a tile -->
                        <div class="tile" draggable="true" data-category="{{ tile['category'] }}" data-special="{{ tile['special'] }}" style="transform: translate(0px, 0px)">
                            {{ tile["word"] }}
                        </div>
                    </div>
                </td>
            {% endfor %}
        </tr>
    {% endfor %}
</table>
```
The answers are in a separate container. They have a class _not-guessed_ and a category equal to a 1-5 or _special_.
```
<div class="answers">
    {% for i in range(5) %}
        <div class="answer not-guessed {% if i > 0 %}category-{{ i - 1}}{% else %}special{% endif %}">
            {{ answers[i] }}
        </div>
    {% endfor %}
</div>
```

### [Create](templates/create.html)
Uses most of the same code as [index.html](#index), but stripped out of any data that is used for gameplay. Each tile and answer contains a _textarea_ that allows for user input. The whole container is a form that collects data from each tile and answer when the _Create_ button is pressed.
```
<textarea required class="input-word" maxlength="40" autocomplete="off" name="word-{{ index }}" placeholder="Word">{{ words[index] }}</textarea>
```
```
<div class="answer {% if i > 0 %}category-{{ i - 1}}{% else %}special{% endif %}">
    <textarea required class="input-answer" maxlength="50" autocomplete="off" name="answer-{{ i }}" placeholder="Answer">{{ answers[i] }}</textarea>
</div>
```

## [Styles](static/styles.css)
All of the styles and animations are declared in this css file.