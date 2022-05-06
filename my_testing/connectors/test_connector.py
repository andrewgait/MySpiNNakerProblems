import pyNN.spiNNaker as p
import matplotlib.pyplot as plt
import numpy as np
p.setup(timestep=1.0)

#p.set_number_of_neurons_per_core(p.IF_cond_exp, 20)
#p.set_number_of_neurons_per_core(p.SpikeSourcePoisson, 80)
#p.set_number_of_neurons_per_core(p.SpikeSourceArray, 20)
n_neurons = 600
model = p.IF_cond_exp
p.set_number_of_neurons_per_core(p.IF_cond_exp, 200)
input = p.Population(n_neurons, p.SpikeSourcePoisson,
                     {'start': 0, 'duration' : 100, 'rate' : 100}, label="input")

#input = p.Population(n_neurons, p.SpikeSourceArray,
#                     {'spike_times': [50]}, label="input")
pop = p.Population(n_neurons, model, {}, label="pop")

synapse = p.StaticSynapse(weight=0.002, delay=1.0)
synapse2 = p.StaticSynapse(weight=0.00005, delay=1.0)
#proj = p.Projection(input, pop, p.FixedProbabilityConnector(15.0/n_neurons),  synapse_type=synapse)
#p.Projection(pop, pop, p.FixedProbabilityConnector(15.0/n_neurons),  synapse_type=synapse2, receptor_type="excitatory")
proj = p.Projection(input, pop, p.FixedNumberPreConnector(15),  synapse_type=synapse)
p.Projection(pop, pop, p.FixedNumberPreConnector(15),  synapse_type=synapse2)

pop.record("spikes")
input.record("spikes")

p.run(100)

print(len(proj.get("weight", format="list"))/n_neurons)
for spiketrain in pop.get_data().segments[0].spiketrains:
    y = np.ones_like(spiketrain) * spiketrain.annotations['source_id']
    plt.plot(spiketrain, y, '.')
plt.show()


p.end()
