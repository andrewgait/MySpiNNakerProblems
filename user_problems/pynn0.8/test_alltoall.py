import spynnaker8 as sim

sim.setup(1.0)

sources = 500
destinations = 500

# onetoone = sim.OneToOneConnector()
alltoall = sim.AllToAllConnector()
# fixedprob = sim.FixedProbabilityConnector(1.0)
# fixedtotal = sim.FixedTotalNumberConnector(200*200)

# spike_times = [[i+1] for i in range(sources)]
# pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times), label="pop1")
pop1 = sim.Population(sources, sim.IF_curr_exp(), label="pop1")
pop2 = sim.Population(destinations, sim.IF_curr_exp(), label="pop2")
synapse_type = sim.StaticSynapse(weight=5, delay=1)
projection = sim.Projection(
    pop1, pop2, alltoall, synapse_type=synapse_type)

sim.run(1)

weights = projection.get(["weight"], "list")
print(weights)
print(len(weights))

sim.end()