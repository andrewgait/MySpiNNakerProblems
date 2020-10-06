import spynnaker8 as p
from pyNN.random import NumpyRNG

p.setup(1.0)
p.set_number_of_neurons_per_core(p.IF_curr_exp, 3)

inp = p.Population(10, p.SpikeSourceArray(spike_times=[1.0]),
                   label="SpikeSourceArray")
out = p.Population(10, p.IF_curr_exp(), label="IF_curr_exp")

rng = NumpyRNG(seed=1235)

weight = p.RandomDistribution("uniform", low=1.0, high=10.0, rng=rng)
delay = 2.0
conn = p.OneToOneConnector()
proj = p.Projection(inp, out, conn,
                    p.StaticSynapse(weight=weight, delay=delay))
proj_stdp = p.Projection(inp, out, conn,
                         p.STDPMechanism(p.SpikePairRule(),
                                         p.AdditiveWeightDependence(),
                                         weight=weight, delay=delay))

weightsdelays_stdp_pre = proj_stdp.get(["weight", "delay"], "list")

p.run(10)

weightsdelays = proj.get(["weight", "delay"], "list")
weightsdelays_stdp_post = proj_stdp.get(["weight", "delay"], "list")

p.end()

print(weightsdelays)
print(weightsdelays_stdp_pre)
print(weightsdelays_stdp_post)
