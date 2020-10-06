import spynnaker8 as sim

sim.setup(1.0)

# Break up the pre population as that is where delays happen
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 50)
pop1 = sim.Population(100, sim.SpikeSourceArray([1]), label="pop1")
pop1b = sim.Population(100, sim.SpikeSourceArray([1]), label="pop1b")
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)
pop2 = sim.Population(10, sim.IF_curr_exp(), label="pop2")
pop2.record("spikes")

# Choose to use delay extensions
synapse_type = sim.StaticSynapse(weight=0.5, delay=17)
synapse_typeb = sim.StaticSynapse(weight=0.3, delay=27)
conn = sim.FixedNumberPreConnector(10)
projection = sim.Projection(
    pop1, pop2, conn, synapse_type=synapse_type)
connb = sim.FixedNumberPreConnector(5)
projectionb = sim.Projection(
    pop1b, pop2, connb, synapse_type=synapse_typeb)
delays = projection.get(["weight", "delay"], "list")
delaysb = projectionb.get(["weight", "delay"], "list")
sim.run(30)

spikes = pop2.get_data("spikes").segments[0].spiketrains
print(delays)
print(sorted(delays, key = lambda x: x[1]))
print(spikes)
print(delaysb)
print(sorted(delaysb, key = lambda x: x[1]))

# There are 100 connections, as there are 10 for each of 10 post-neurons
assert(len(delays) == 100)  # 40)  # 100)
assert(len(delaysb) == 50)

# If the delays are done right, all pre-spikes should arrive at the
# same time causing each neuron in the post-population to spike
for s in spikes:
    assert(len(s) == 1)

sim.end()