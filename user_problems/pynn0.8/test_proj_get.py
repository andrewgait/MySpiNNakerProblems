import spynnaker8 as sim

sources = 2
destinations = 3

sim.setup(1.0)

pop1 = sim.Population(
    sources, sim.SpikeSourceArray(spike_times=[0]), label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(), label="pop2")

synapse_type = sim.StaticSynapse(weight=5, delay=2)

projection = sim.Projection(
    pop1, pop2, sim.OneToOneConnector(), synapse_type=synapse_type)
# projection = sim.Projection(
#     pop1, pop2, sim.FromListConnector([[0,0]]), synapse_type=synapse_type)

from_pro = projection.get(["weight", "delay"], "list")

sim.run(1)

print(len(from_pro))

sim.end()