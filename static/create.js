const tiles = document.querySelectorAll('.tile, .answer')

let count = 0

tiles.forEach(tile => {
    tile.addEventListener('dragstart', () => {
        tile.classList.add('dragging')
    })

    // Move the tile if it is dragged to another slot
    tile.addEventListener('dragend', () => {

        tile.classList.remove('dragging')
        const closest = document.querySelector('.closest')
        
        if (closest) {
            closest.classList.remove('closest')

            if (closest != tile) {
                // Perform the swap
                let temp = tile.children[0].value;
                tile.children[0].value = closest.children[0].value;
                closest.children[0].value = temp;
            }
        }
    })

    tile.addEventListener('dragover', event => {
        event.preventDefault()
        tile.classList.add('closest')
    })
    tile.addEventListener('dragleave', event => {
        tile.classList.remove('closest')
    })
})