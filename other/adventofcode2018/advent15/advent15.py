# Advent of code, day 15

# open file
#input = open("advent15_input.txt", "r")
input = open("advent15_test_input_target.txt", "r")

game_status = []
units = []
hp = 200

order = 1
# read string into array
for line in input:
    game_line = []
    for i in range(len(line)):
        if (line[i] != "\n"):
            game_line.append(line[i])
        if (line[i] == "E"):
            units.append(["E",i,len(game_status),order,hp])
            order += 1
        if (line[i] == "G"):
            units.append(["G",i,len(game_status),order,hp])
            order += 1

    game_status.append(game_line)


# define a function to print the grid
def print_grid(grid):
    # make sure a grid can be printed
    for j in range(len(grid)):
        line_string = ''
        for i in range(len(grid[j])):
            line_string += grid[j][i]

        print(line_string)


# define a function to get goblins and elves from units
def get_goblins_and_elves(units):
    goblins = []
    elves = []
    for i in range(len(units)):
        if (units[i][0] == "E"):
            elves.append(units[i])
        elif (units[i][0] == "G"):
            goblins.append(units[i])

    return goblins, elves


# define a function to get a distance grid from a coordinate
def get_distance_grid(grid, x, y):
    distance_grid = []
    for j in range(grid)


    return distance_grid

# define function to move unit
def move_unit(unit, grid, enemies):
    xu = unit[1]
    yu = unit[2]
    print(xu, yu)

    potential_target_squares = []
    # loop over enemies, print . location
    for n in range(len(enemies)):
        xe = enemies[n][1]
        ye = enemies[n][2]
        # visit possible squares in "reading order"
        if (grid[ye-1][xe] == "."):
            potential_target_squares.append([xe,ye-1])
        if (grid[ye][xe-1] == "."):
            potential_target_squares.append([xe-1,ye])
        if (grid[ye][xe+1] == "."):
            potential_target_squares.append([xe+1,ye])
        if (grid[ye+1][xe] == "."):
            potential_target_squares.append([xe,ye+1])

    print('unit: ', unit, ' target_squares: ', potential_target_squares)
    # which of these squares are reachable at present?
    # and which of the reachable squares is closest (tie: reading order)
    reachable_squares = []
    for m in range(len(potential_target_squares)):
        # make a distance grid for this target square
        xt = potential_target_squares[m][0]
        yt = potential_target_squares[m][1]
        distance_grid = get_distance_grid(grid, xt, yt)

        # now this has been done, are any of the squares next to the unit




    return 'hello'

print_grid(game_status)
print('units: ', units)

combat_round = 1
combat_continues = True
while (combat_continues):
    goblins, elves = get_goblins_and_elves(units)
    print('elves: ', elves)
    print('goblins: ', goblins)

    # loop over units
    for n in range(len(units)):
        # move this unit
        if (units[n][0] == "E"):
            print(move_unit(units[n], game_status, goblins))
        elif (units[n][0] == "G"):
            print(move_unit(units[n], game_status, elves))

    combat_continues = False
