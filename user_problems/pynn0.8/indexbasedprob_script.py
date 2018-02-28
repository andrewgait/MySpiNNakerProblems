import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

p.setup(timestep=1.0)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -40.0
                   }


#def create_grid(n, label, dx=1.0, dy=1.0):
#    grid_structure = p.Grid2D(dx=dx, dy=dy, x0=0.0, y0=0.0)
#    return p.Population(n*n, p.IF_curr_exp(**cell_params_lif),
#                        structure=grid_structure, label=label)


n = 10
# tau_exc = 1.0
# tau_inh = 1.0
weight_to_spike = 3.0
delay = 2
runtime = 200

# Network
# grid = create_grid(n, 'grid')

pop_1 = p.Population(n*n, p.IF_curr_exp(**cell_params_lif), label='pop_1')

# SpikeInjector
injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
inj_pop = p.Population(1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1')

p.Projection(inj_pop, pop_1, p.FromListConnector(injectionConnection),
             p.StaticSynapse(weight=weight_to_spike, delay=delay))

# Connectors
index_based_exc = "(i+j)/200.0"
index_based_inh = "(i+j)/400.0"
#dist_dep_exc = "exp(-d)/{tau_exc}".format(tau_exc=tau_exc)
#dist_dep_inh = 'exp(-0.5*d)/{tau_inh}'.format(tau_inh=tau_inh)

exc_connector = p.IndexBasedProbabilityConnector(
    index_based_exc, allow_self_connections=True)

inh_connector = p.IndexBasedProbabilityConnector(
    index_based_inh, allow_self_connections=False)

# Wire grid
p.Projection(pop_1, pop_1, exc_connector,
             p.StaticSynapse(weight=4.0, delay=5))
p.Projection(pop_1, pop_1, inh_connector,
             p.StaticSynapse(weight=3.5, delay=10))

pop_1.record(['v','spikes'])

p.run(runtime)

v = pop_1.get_data('v')
spikes = pop_1.get_data('spikes')

Figure(
    # raster plot of the presynaptic neurons' spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=2.0, xlim=(0, runtime), xticks=True),
    # membrane potential of the postsynaptic neurons
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime), xticks=True),
    title="Simple index-based prob connector",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()