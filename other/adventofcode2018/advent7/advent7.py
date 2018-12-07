# Advent of code, day 7

# open file
input = open("advent7_test_input.txt", "r")
alphabet = 'ABCDEF'
n_workers = 2
set_time = 1

# input = open("advent7_input.txt", "r")
# alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# n_workers = 5
# set_time = 61


array_sets = []
original_array_sets = []
counted = []
time_task = []
for n in range(len(alphabet)):
    array_sets.append(set())
    original_array_sets.append(set())
    counted.append(0)
    time_task.append(set_time+n)

print(time_task)

# read string into array
for line in input:
    # 9 spaces
    data = line.rsplit(' ', 9)
    step = data[1]
    next_step = data[7]

    n = alphabet.index(next_step)
    # print(n)
    array_sets[n].add(step)
    original_array_sets[n].add(step)

print(array_sets)

# part 2 (comment out to make part 1 work)
entries = True
final_string = ''
work_array = []
time_left = []
currently_working = []
for n in range(n_workers):
    work_array.append([])
    time_left.append(0)
    currently_working.append(0)

previous_string = ''
n_working = 0
time = 0
while entries:
    count_empty = 0
    this_string = ''
    for n in range(len(array_sets)):
        if (len(array_sets[n]) == 0):
            count_empty += 1
            if (counted[n] == 0):
                counted[n] = 1
                this_string += alphabet[n]

    # find the time length for this task and add it
    print('this_string: ', this_string)

    tasks = len(this_string)

    # working on stuff?
    workers = True
    while workers:
        # is there a task available?
        if (tasks > 0):
            for i in range(len(this_string)):
                # is there a free worker?
                if (n_working < n_workers):
                    index = alphabet.index(this_string[i])
                    time_left[n_working] = time_task[index]
                    currently_working[n_working] = 1
                    n_working += 1
                    tasks -= 1
                    workers = True
        else:
            for i in range(n_workers):
                if (currently_working[i] == 1):
                    time_left[i] -= 1
                    if (time_left[i] == 0):
                        n_working -= 1
                        currently_working[i] = 0
                        # workers = False
                        # task_completed[index] = True

        print(time_left)

        sum_working = 0
        for i in range(n_workers):
            sum_working += currently_working[i]

        if (sum_working == 0):
            workers = False

        time += 1

    print('time: ', time)

    # remove all instances from each set
    for n in range(len(alphabet)):
        for m in range(len(this_string)):
            try:
                array_sets[n].remove(this_string[m])
            except:
                blah = []


    print(array_sets)

    time += 1

    if (count_empty == len(array_sets)):
        entries = False

print('time: ', time)

# comment out to here for part 1 to work

# part 1
# entries = True
# final_string = ''
# while entries:
#     # find the first entry that is empty
#     count_empty = 0
#     for n in range(len(array_sets)):
#         if (len(array_sets[n]) == 0):
#             count_empty += 1
#             # has it not been counted yet
#             if (counted[n] == 0):
#                 # count it, and append to final string now
#                 counted[n] = 1
#                 final_string += alphabet[n]
#                 # remove all instances from each set
#                 for m in range(len(array_sets)):
#                     try:
#                         array_sets[m].remove(alphabet[n])
#                     except:
#                         blah = []
#                         # print('not here')
#                 break
#
#     print(final_string)
#
#     if (count_empty == len(array_sets)):
#         entries = False







