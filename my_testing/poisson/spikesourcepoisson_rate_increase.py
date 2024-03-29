"""
script finding timeout with rate increase
"""

import pyNN.spiNNaker as p

p.setup(1.0)
inp = p.Population(40, p.SpikeSourcePoisson(rate=2),
                   additional_parameters={"seed": 417},
                   label = "input")
inp.record("spikes")
p.run(100)
p.reset()
inp.set(rate=30)
p.run(100)
