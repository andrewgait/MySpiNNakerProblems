import parsl
import os
from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor
from parsl.app.app import python_app, bash_app

local_threads = Config(
    executors=[
        ThreadPoolExecutor(
            max_threads=4,
            label='local_threads'
        )
    ]
)

parsl.clear()
parsl.load(local_threads)

@bash_app
def generate(outputs=[]):
    return "echo $(( RANDOM )) &> {outputs[0]}"

@bash_app
def concat(inputs=[], outputs=[]):
    return "cat {0} > {1}".format(" ".join(inputs), outputs[0])

@python_app
def total(inputs=[]):
    total = 0
    with open(str(inputs[0]), 'r') as f:
        for l in f:
            total += int(l)
    return total

# Create 5 files with semi-random numbers
output_files = []
for i in range (5):
     output_files.append(generate(outputs=[os.path.join(os.getcwd(), 'random-%s.txt' % i)]))

# Concatenate the files into a single file
cc = concat(inputs=[i.outputs[0].filepath for i in output_files],
            outputs=[os.path.join(os.getcwd(), 'combined.txt')])

# Calculate the sum of the random numbers
total = total(inputs=[cc.outputs[0]])

print(total.result())