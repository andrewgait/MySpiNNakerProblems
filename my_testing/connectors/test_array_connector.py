import pyNN.spiNNaker as p
import numpy as np

p.setup(timestep=1.0)

n_i = 64
n_e = 64

spikeArray = {'spike_times': [0]}
input_pop = p.Population(n_e, p.SpikeSourceArray(**spikeArray),
                        label='inputSpikes')
excit_pop = p.Population(n_e, p.IF_curr_exp, label='excit')
inhit_pop = p.Population(n_i, p.IF_curr_exp, label='inhib')
input_projec = p.Projection(input_pop, excit_pop, p.AllToAllConnector(),
                            synapse_type=p.StaticSynapse(weight=5), receptor_type='excitatory')

ie_conn = np.ones((n_i, n_e))
for i in range(n_e):
    ie_conn[i, i] = 0

print("connections: ", ie_conn)

ei_projec = p.Projection(excit_pop, inhit_pop, p.OneToOneConnector(),
                         synapse_type=p.StaticSynapse(weight=2))

ie_projec = p.Projection(inhit_pop, excit_pop, p.ArrayConnector(ie_conn),
                         synapse_type=p.StaticSynapse(weight=3))

p.run(1000)

p.end()