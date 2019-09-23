"""
script trying infinite run out...
"""

import spynnaker8 as p

p.setup(1.0)
cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }
inp = p.Population(40, p.IF_curr_exp(**cell_params_lif),
                   label = "input")
inp.record("spikes")
p.run(None)

p.end()