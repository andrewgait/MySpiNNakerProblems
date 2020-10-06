import spynnaker8 as sim
import numpy as np

sim.setup(timestep=1.0, min_delay=1, max_delay=144)

n_pop = 2550  # 128*128  # 513
list_size = 2500  # 128*128  # 500
runtime = 100

# input_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="input")
input_pop = sim.Population(n_pop, sim.SpikeSourceArray(spike_times=[0]), label="input")
out_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="out_pop")

list1 = []
for i in range(list_size):
    list1.append((i, i, 0.001, 1))

list1.append((200, 0, 9.0, 10))

np.save('list.npy', list1)

fromlist_in2out = sim.FromListConnector(list1)

proj_in2out = sim.Projection(input_pop, out_pop, fromlist_in2out,
                             receptor_type='excitatory',
                             synapse_type=sim.StaticSynapse(weight=0.5,
                                                            delay=1.0))

sim.run(runtime)

print(proj_in2out.get(["weight", "delay"], "list"))

sim.end()
