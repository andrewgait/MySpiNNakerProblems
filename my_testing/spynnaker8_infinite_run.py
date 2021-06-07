"""
script trying infinite run out...
"""

import spynnaker8 as p

p.setup(1.0)
inp = p.Population(40, p.IF_curr_exp(),label = "input")
inp.record("spikes")
p.run(None)

p.end()