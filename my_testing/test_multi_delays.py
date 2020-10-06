import spynnaker8 as sim

n_neurons = 50
sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 100)

pop_1 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_1")
input = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, 3000, 100)),
    label="input")
proj1 = sim.Projection(
    input, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5, delay=1))
proj2 = sim.Projection(
    input, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5, delay=20))
proj3 = sim.Projection(
    input, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5, delay=40))
proj4 = sim.Projection(
    input, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5, delay=60))
proj5 = sim.Projection(
    input, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5, delay=80))
pop_1.record(["spikes"])
sim.run(3000)

spikes = pop_1.spinnaker_get_data("spikes")

print(proj1.get(['weight', 'delay'], 'list'))
print(proj2.get(['weight', 'delay'], 'list'))
print(proj3.get(['weight', 'delay'], 'list'))
print(proj4.get(['weight', 'delay'], 'list'))
print(proj5.get(['weight', 'delay'], 'list'))

print(len(spikes))



sim.end()

