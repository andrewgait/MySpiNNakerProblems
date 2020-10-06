import spynnaker8 as sim
from pyNN.random import NumpyRNG

sim.setup(timestep=1.0)

in_pop = sim.Population(4, sim.SpikeSourceArray([0]), label="in_pop")
pop = sim.Population(4, sim.IF_curr_exp(), label="pop")
rng = NumpyRNG(seed=2)
conn = sim.Projection(in_pop[0:3], pop[1:4],
                      sim.FixedNumberPreConnector(2, rng=rng),
                      sim.StaticSynapse(weight=0.5, delay=2))

sim.run(1)
weights = conn.get(['weight', 'delay'], 'list')
sim.end()

print("weights: ", weights)

# The fixed seed means this gives the same answer each time
target = [(0, 1, 0.5, 2.0), (1, 2, 0.5, 2.0), (1, 3, 0.5, 2.0),
          (2, 1, 0.5, 2.0), (2, 2, 0.5, 2.0), (2, 3, 0.5, 2.0)]
print("target: ", target)