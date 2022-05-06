import pyNN.spiNNaker as sim

sim.setup(1.0)

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 99)
pop = sim.Population(5, sim.IF_curr_exp(), {}, label="pop")
synapse_type = sim.StaticSynapse(weight=5, delay=1)
connector = sim.FixedTotalNumberConnector(40, with_replacement=False)
projection = sim.Projection(
    pop, pop, connector, synapse_type=synapse_type)

sim.run(0)

weights = projection.get(["weight"], "list")
print(weights)
print(len(weights))

sim.end()