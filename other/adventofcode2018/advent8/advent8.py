# Advent of code, day 8

# open file
#input = open("advent8_input.txt", "r")
input = open("advent8_test_input.txt", "r")

# read string into array
for line in input:
    # count the number of spaces
    spaces = line.count(' ')
    print(spaces)
    data = line.rsplit(' ', spaces)

size = len(data)
print(size)

def read_header_and_sum(data, sum):
    print(data)
    children = int(data[0])
    entries = int(data[1])
    data = data[2:]
    for i in range(children):
        sum += read_header_and_sum(data, sum)

    for j in range(entries):
        sum += int(data[j])

    print('sum: ', sum)
    data = data[entries:]
    return sum

sum = 0
total = read_header_and_sum(data, sum)

print('sum total is ', total)
