import spynnaker8 as sim

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 50)

pop_1 = sim.Population(400, sim.IF_curr_exp(), label="pop_1")
input = sim.Population(400, sim.SpikeSourceArray(spike_times=[0]), label="input")

input_proj = sim.Projection(input, pop_1, sim.OneToOneConnector(),
                            synapse_type=sim.StaticSynapse(weight=5, delay=1))

pop_1.record(["spikes", "v"])

simtime = 10
sim.run(simtime)
neo = pop_1.get_data(variables=["spikes", "v"])

sim.end()

spikes = neo.segments[0].spiketrains
print(spikes)
v = neo.segments[0].filter(name='v')[0]
print(v)