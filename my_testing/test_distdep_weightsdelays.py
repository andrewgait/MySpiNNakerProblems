import spynnaker8 as p
from pyNN.random import NumpyRNG
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


def create_grid(n, label, dx=1.0, dy=1.0):
    grid_structure = p.Grid2D(dx=dx, dy=dy, x0=0.0, y0=0.0)
    return p.Population(n*n, p.IF_curr_exp(**cell_params_lif),
                        structure=grid_structure, label=label)


n = 4
# tau_exc = 1.0
# tau_inh = 1.0
weight_to_spike = 5.0
delay = 2
runtime = 200

# Network
grid = create_grid(n, 'grid')
grid2 = create_grid(3, 'grid', dx=1.0, dy=2.0)

# SpikeInjector
injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
inj_pop = p.Population(1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1')

p.Projection(inj_pop, grid, p.FromListConnector(injectionConnection),
             p.StaticSynapse(weight=weight_to_spike, delay=5))

# Connectors
exc_connector = p.AllToAllConnector()
# inh_connector = p.AllToAllConnector()
inh_connector = p.FixedProbabilityConnector(0.5, rng=NumpyRNG(seed=10101))

# Wire grid
exc_proj = p.Projection(grid, grid, exc_connector,
                        p.StaticSynapse(weight="2.0 + 2.0*d", delay=5))
inh_proj = p.Projection(grid, grid, inh_connector,
                        p.StaticSynapse(weight=1.5, delay="3.0 + 3.0*d"))

exc_proj2 = p.Projection(grid2, grid2, exc_connector,
                         p.StaticSynapse(weight="1.5 + 1.5*d", delay=8))

grid.record(['v','spikes'])

p.run(runtime)

v = grid.get_data('v')
spikes = grid.get_data('spikes')

exc_conns = exc_proj.get(['weight', 'delay'], 'array')
print(exc_conns)
inh_conns = inh_proj.get(['weight', 'delay'], 'array')
print(inh_conns)
inh_conns_list = inh_proj.get(['weight', 'delay'], 'list')
print(inh_conns_list)
exc_conns_list = exc_proj.get(['weight', 'delay'], 'list')
print(exc_conns_list)
exc2_conns_list = exc_proj2.get(['weight', 'delay'], 'list')
print(exc2_conns_list)

Figure(
    # raster plot of the presynaptic neurons' spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, runtime), xticks=True),
    # membrane potential of the postsynaptic neurons
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[grid.label], yticks=True, xlim=(0, runtime), xticks=True),
    title="Simple 2D grid distance-dependent weights and delays",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()