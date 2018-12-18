# Advent of code, day 18

# open file
#input = open("advent18_input.txt", "r")
input = open("advent18_test_input.txt", "r")


def char_from_val(val):
    characters = [".", "#", "|"]
    return characters[val]


def val_from_char(char):
    characters = [".", "#", "|"]
    return characters.index(char)


def render_grid(grid):
    # render grid
    for j in range(len(grid)):
        str_line = ''
        for i in range(len(grid[j])):
            str_line += char_from_val(grid[j][i])

        print(str_line)

    print(' ')

# three functions for changing based on the character
# the grid will be built so that the loop is over the interior
def change_open(grid, x, y):
    sumtree = 0
    # loop over the grid, count trees


def change_tree(grid, x, y):
    sumlumber = 0
    # loop over the grid, count lumberyards


def change_lumberyard(grid, x, y):
    sumtree = 0
    sumlumber = 0
    # loop over the grid, count trees and lumberyards



grid = []
# read string into array
# what should happen here is that a ring of "."
# should be added around the whole grid as a halo,
# and this will deal with issues re: corner/edge cases
for line in input:
    gridline = []
    for n in range(len(line)):
        if (line[n] == "."):
            gridline.append(val_from_char("."))
        elif (line[n] == "|"):
            gridline.append(val_from_char("|"))
        elif (line[n] == "#"):
            gridline.append(val_from_char("#"))

    grid.append(gridline)


render_grid(grid)

time = 10

while (time <= 10):
    new_grid = []

    # not sure if this needs to be
    grid = new_grid
    render_grid(grid)
    time += 1

render_grid(grid)

# final grid calculation
