import pyNN.spiNNaker as sim
import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import csv
from pyNN.utility.plotting import Figure, Panel

# Create spike array
batch_size = 1
data_width = 720
data_height = 510
spike_array = [[] for _ in range(data_height*data_width)]
file_non_pushing = "16_1619081021736.csv"
file_pushing = "500_1619081032105.csv"
for classs in range(batch_size):
    if classs == 0:
        file_csv = file_non_pushing
    if classs == 1:
        file_csv = file_pushing
    file = "/localhome/mbbssag3/Downloads/"+str(file_non_pushing)
    print(file)
    if os.path.isfile(file):
        # read the .csv file
        f = open(file, newline='')
        reader = csv.reader(f, delimiter=",")
        # jump the headers
        next(reader)
        data = []
        data = np.array(list(reader))[:, :]
        data = data.astype(np.int)
        data_size = data.shape[0]
    # adjust size of array to the new frame size
    data_point_spike_array = [[] for _ in range(510*720)]
    # data_size = 800*1280
    for d in range(data_size):
        if data[d,4] == 1:
            if data[d, 0] < data_height and data[d, 1] >= 280 and data[d, 1] < 280 + data_width:
                time = data[d, 3]//1000
                index = (data[d, 0]*data_width)+(data[d, 1]-280)
                data_point_spike_array[index].append(time)
    idx_sa = 0
    for sa,dpsa in zip(spike_array,data_point_spike_array):
        spike_array[idx_sa] = sa+dpsa
        idx_sa+=1

# Check data
num_events=0
for i in spike_array:
    num_events+=len(i)
print("Number of events is "+str(num_events))
print("Max value is "+str(max(max(spike_array))))

# print(spike_array)
print(len(spike_array))
total_average = []
for i in range(len(spike_array)):
    if len(spike_array[i]) > 0:
        print(i, spike_array[i])
        spike_array[i] = np.sort(spike_array[i])
        average = np.median(spike_array[i])
        if average != 0:
            total_average.append(average)
print(np.median(total_average))
print(min(total_average))

# Setup the Simulator
sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 50)

# Create the neural populations
width = 720
height = 510
neurons = width*height
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, neurons // 8)
input = sim.Population(neurons, sim.SpikeSourceArray(spike_array))
pop_1 = sim.Population(neurons, sim.IF_curr_exp())

# Create projections between the populations
sim.Projection(input, pop_1, sim.OneToOneConnector(), sim.StaticSynapse(weight=5, delay=1))

# Setup data recording
pop_1.record("spikes")

# Run the simulation
sim.run(1000)

# Retrieve and process the recorded data
spikes = pop_1.get_data("spikes")
#print(spikes.segments[0].spiketrains)

sim.end()

#Plot graph
#Figure(Panel(spikes.segments[0].spiketrains))

#Plot graph
Figure(
    Panel(spikes.segments[0].spiketrains, xlim=[800,900],
          xlabel="Time", xticks=True, ylabel="index", yticks=True),
    title="SSA (Rodrigues data)",
    annotations="Simulated with {}".format(sim.name())
)

#plt.show()
plt.savefig("test_ssa.png")

