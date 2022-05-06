import pyNN.spiNNaker as sim
import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 2)
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 2)

pop_1 = sim.Population(4, sim.IF_curr_exp(), label="pop_1")
input = sim.Population(10, sim.SpikeSourceArray(spike_times=[0]), label="input")
input_proj = sim.Projection(input, pop_1, sim.OneToOneConnector(),
                            synapse_type=sim.StaticSynapse(weight=5, delay=21))

sim.run(40)