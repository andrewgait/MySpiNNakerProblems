# Advent of code, day 8

# open file
#input = open("advent8_input.txt", "r")
input = open("advent8_test_input.txt", "r")

data = []
# read string into array
for line in input:
    # count the number of spaces
    spaces = line.count(' ')
    print(spaces)
    data = line.rsplit(' ', spaces)

size = len(data)
print(size)

node_val_array = []

def read_header_and_sum():
    global data
    global sum
    global node_val_array
#    print(data)
    children = int(data[0])
    entries = int(data[1])
    data = data[2:]

    for i in range(children):
        read_header_and_sum()

    for j in range(entries):
        sum += int(data[j])

    print('sum: ', sum)
    data = data[entries:]

sum = 0
read_header_and_sum()

print('sum total is ', sum)
print('len(data) is ', len(data))
