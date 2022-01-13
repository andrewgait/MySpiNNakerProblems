import spynnaker8 as sim

sources = 20000
destinations = 2000


sim.setup(1.0)
pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times=[0]),
                      label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(),
                      label="pop2")
delays = sim.RandomDistribution("uniform", [2, 12])
synapse_type = sim.StaticSynapse(weight=5, delay=delays)

# connector = sim.OneToOneConnector()
connector = sim.AllToAllConnector()
# connector = sim.FromListConnector([(1, 2), (0, 1)])
projection = sim.Projection(pop1, pop2, connector,
                            synapse_type=synapse_type)
#projection = sim.Projection(pop1, pop2, sim.FromListConnector([[0,0]]),
#                            synapse_type=synapse_type)
# sim.run(0)
# before_pro = projection.get(["weight", "delay"], "list")
# print('projection.get was called before run')
sim.run(1)
after_pro = projection.get(["weight", "delay"], "list")

# print(before_pro)
#print(len(before_pro))
# print(after_pro)
print(len(after_pro))
print(after_pro[0], after_pro[-1])

sim.end()