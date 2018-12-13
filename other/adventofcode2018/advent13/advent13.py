# Advent of code, day 13
from _ast import Or

# open file
#input = open("advent13_input.txt", "r")
input = open("advent13_test_input1.txt", "r")


def get_val(string):
    string_array = ["-", "|", "/", "\\", "+", " ", ">", "<", "v", "^"]
    return string_array.index(string)


def get_string(val):
    string_array = ["-", "|", "/", "\\", "+", " ", ">", "<", "v", "^"]
    return string_array[val]


def print_grid(current_grid):
#    for n in (len(cart_coords)):
#        current_grid[cart_coords[n][0], cart_coords[n][1]] = cart_coords[n][2]

    # loop
    for j in range(len(current_grid)):
        grid_string = ''
        for i in range(len(current_grid[j])):
            grid_string += current_grid[j][i]

        print(grid_string)

    # add a blank line at the end
    print(' ')


current_grid = []
cart_coords = []

max_line_length = 0
# read string into array
for line in input:
    #
    if (len(line) > max_line_length):
        max_line_length = len(line)
    # is there a cart on this line?
    # remember the last character of each line except the last is a newline
    for i in range(len(line)-1):
        if ((line[i] == ">") or (line[i] == "<")):
            # mark coordinate
            cart_coords.append([i,len(current_grid),line[i],"l"])
            # replace the value with a -
            #line[i] = "-"
        elif ((line[i] == "^") or (line[i] == "v")):
            # mark coordinate
            cart_coords.append([i,len(current_grid),line[i],"l"])
            # replace the value with a |
            #line[i] = "|"

        data.append()

    current_grid.append(line)


print_grid(current_grid)
print(cart_coords)

print(current_grid)

# loop over carts
for n in range(len(cart_coords)):
    # update the grid accordingly
    x = cart_coords[n][0]
    y = cart_coords[n][1]
    type = cart_coords[n][2]
    next_turn = cart_coords[n][3]

    old_type = type
    # I'm sure this can be simplified but it's not easy to see how
    if (type == ">"):
        # replace with -
        current_grid[y][x] = "-"
        x += 1
        if (current_grid[y][x] == "/"):
            # left turn, so new cart direction is ^
            type = "^"
        elif (current_grid[y][x] == "\\"):
            # right turn, so new cart direction is v
            type = "v"
        elif (current_grid[y][x] == "+"):
            # turn depending on the value of next_turn
            if (next_turn == "l"):
                type = "^"
                next_turn = "s"
            elif (next_turn == "r"):
                type = "v"
                next_turn = "l"
            else:
                # next_turn goes from s to r, type doesn't change
                next_turn = "r"
    elif (type == "<"):
        # replace with -
        current_grid[y][x] += "-"
        x -= 1
        if (current_grid[y][x] == "/"):
            # left turn, so new cart direction is v
            type = "v"
        elif (current_grid[y][x] == "\\"):
            # right turn, so new cart direction is ^
            type = "^"
        elif (current_grid[y][x] == "+"):
            # turn depending on the value of next_turn
            if (next_turn == "l"):
                type = "v"
                next_turn = "s"
            elif (next_turn == "r"):
                type = "^"
                next_turn = "l"
            else:
                # next_turn goes from s to r, type doesn't change
                next_turn = "r"
    elif (type == "^"):
        # replace with |
        current_grid[y][x] += "|"
        y -= 1
        if (current_grid[y][x] == "/"):
            # right turn, so new cart direction is >
            type = ">"
        elif (current_grid[y][x] == "\\"):
            # left turn, so new cart direction is <
            type = "<"
        elif (current_grid[y][x] == "+"):
            # turn depending on the value of next_turn
            if (next_turn == "l"):
                type = "<"
                next_turn = "s"
            elif (next_turn == "r"):
                type = ">"
                next_turn = "l"
            else:
                # next_turn goes from s to r, type doesn't change
                next_turn = "r"
    elif (type == "v"):
        # replace with |
        current_grid[y][x] += "|"
        y += 1
        if (current_grid[y][x] == "/"):
            # right turn, so new cart direction is <
            type = "<"
        elif (current_grid[y][x] == "\\"):
            # left turn, so new cart direction is >
            type = ">"
        elif (current_grid[y][x] == "+"):
            # turn depending on the value of next_turn
            if (next_turn == "l"):
                type = ">"
                next_turn = "s"
            elif (next_turn == "r"):
                type = "<"
                next_turn = "l"
            else:
                # next_turn goes from s to r, type doesn't change
                next_turn = "r"

    # nothing else changes
    current_grid[y][x] += type

    cart_coords[n][0] = x
    cart_coords[n][1] = y
    cart_coords[n][2] = type
    cart_coords[n][3] = next_turn


print_grid(current_grid)
print(cart_coords)
