import spynnaker8 as sim

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 100)

input = sim.Population(1, sim.SpikeSourceArray(spike_times=[0]),
                           label="input")
pop_1 = sim.Population(200, sim.IF_curr_exp(), label="pop_1")

sim.Projection(input, pop_1, sim.AllToAllConnector(),
               synapse_type=sim.StaticSynapse(weight=5, delay=18))

sim.run(500)
