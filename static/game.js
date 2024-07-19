const game = document.querySelector('.game')
const tiles = document.querySelectorAll('.tile')
const slots = document.querySelectorAll('.slot')
const popup = document.getElementById("popup")

const answerSpecial = document.querySelector('.answer.special')
const answers = [
    document.querySelector('.answer.category-0'),
    document.querySelector('.answer.category-1'),
    document.querySelector('.answer.category-2'),
    document.querySelector('.answer.category-3')
]

const maxMoves = 15
let movesMade = 0
let solved = false

updateTiles()
countMove(true)

function updateTiles()
{
    let categories_solved = 0
    // Loop through all the basic categories
    for (let c = 0; c < 4; c++) {
        let tiles = document.querySelectorAll(`[data-category="${c}"]`)

        // Reset the color of each tile
        tiles.forEach( tile => {
            tile.classList.remove('category-' + tile.dataset.category)
            tile.classList.remove('special')
            tile.classList.remove('almost')
        })

        // Update the colors
        if (updateCategory(tiles)) {
            answers[c].classList.remove('not-guessed')
            answers[c].classList.add('guessed')
            categories_solved += 1
        }

    }

    // Set the color for the special category
    let specialTiles = document.querySelectorAll("[data-special='True']")
    if (updateCategory(specialTiles, true)) {
        answerSpecial.classList.remove('not-guessed')
        answerSpecial.classList.add('guessed')
        categories_solved += 1
    }
    
    if (categories_solved == 5) {
        solved = true
        animateVictory()
    }
}


function updateCategory(tiles, special=false)
{
    // Loop through each row and column and update colors
    for (let i = 0; i < 4; i++) {
        let row = [...tiles].filter(tile => tile.parentNode.dataset.x === i.toString())
        let col = [...tiles].filter(tile => tile.parentNode.dataset.y === i.toString())
        if (updateLine(row, special) || updateLine(col, special)) {
            return true
        }
    }
    return false
}

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

// Count the moves
function countMove(reset=false) {
    if (solved) {
        return
    }

    if (reset) {
        movesMade = 0
    } else {
        movesMade = movesMade + 1
    }

    if (maxMoves - movesMade == 1) {
        popup.classList.toggle("show")
    } else if (movesMade >= maxMoves) {
        tiles.forEach(tile => {
            tile.setAttribute('draggable', false)
        })
    }
    document.getElementById('counter').innerText = 'Moves made: ' + movesMade + '/' + maxMoves
}

tiles.forEach(tile => {
    const category = tile.dataset.category

    tile.addEventListener('dragstart', event => {
        tile.classList.add('dragging')
    })

    // Move the tile if it is dragged to another slot
    tile.addEventListener('dragend', () => {
        tile.classList.remove('dragging')
        if (movesMade >= maxMoves) {
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
})

// Make slots detect when there is something dragged over them
slots.forEach(slot => {
    slot.addEventListener('dragover', event => {
        event.preventDefault()
        slot.classList.add('closest')
    })
    slot.addEventListener('dragleave', event => {
        slot.classList.remove('closest')
    })
})

// Hide the popup after the animation ends
popup.addEventListener('animationend', event => {
    if (event.animationName == 'fadeOut'){
        popup.classList.toggle('show')
    }
});


// Animate victory
function animateVictory() {
    let remaining = [...document.querySelectorAll('.tile')]
    remaining.forEach( tile => {
        tile.addEventListener('animationend', () => animateTile(remaining), { once: true })
    })
    setTimeout(animateTile, 500, remaining)
}

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