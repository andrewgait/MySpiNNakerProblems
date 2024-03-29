import pyNN.spiNNaker as p
from spynnaker.pyNN.utilities import neo_convertor

p.setup(timestep=1.0, min_delay=1.0)

cell_params = {'i_offset': .1, 'tau_refrac': 3.0, 'v_rest': -65.0,
               'v_thresh': -51.0, 'tau_syn_E': 2.0,
               'tau_syn_I': 5.0, 'v_reset': -70.0,
               'e_rev_E': 0., 'e_rev_I': -80.}

# setup test population
if_pop = p.Population(1, p.IF_cond_exp, cell_params)
# setup spike sources
spike_times = [20., 40., 60.]
exc_pop = p.Population(1, p.SpikeSourceArray,
                       {'spike_times': spike_times})
inh_pop = p.Population(1, p.SpikeSourceArray,
                       {'spike_times': [120, 140, 160]})
# setup excitatory and inhibitory connections
listcon = p.FromListConnector([(0, 0, 0.05, 1.0)])
p.Projection(exc_pop, if_pop, listcon, receptor_type='excitatory')
p.Projection(inh_pop, if_pop, listcon, receptor_type='inhibitory')
# setup recorder
if_pop.record(["v"])
p.run(100)
p.reset()
if_pop.initialize(v=-65)
exc_pop.set(spike_times=[])
inh_pop.set(spike_times=spike_times)
p.run(100)
# read out voltage and plot
neo = if_pop.get_data("all")
p.end()
v = neo_convertor.convert_data(neo, "v", run=0)
v2 = neo_convertor.convert_data(neo, "v", run=1)
