import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy
import csa

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


# def create_grid(n, label, dx=1.0, dy=1.0):
#     grid_structure = p.Grid2D(dx=dx, dy=dy, x0=0.0, y0=0.0)
#     return p.Population(n*n, p.IF_curr_exp(**cell_params_lif),
#                         structure=grid_structure, label=label)


n = 13 # 10  # 5
p.set_number_of_neurons_per_core(p.IF_curr_exp, n)
# tau_exc = 1.0
# tau_inh = 1.0
weight_to_spike = 2.0
delay = 2
runtime = 200

# Network
# grid = create_grid(n, 'grid')
grid = csa.grid2d(n, xScale=1.0*n, yScale=1.0*n)
csa.gplot2d(grid, n*n)

# SpikeInjector
injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}
inj_pop = p.Population(1, p.SpikeSourceArray(**spikeArray),
                       label='inputSpikes_1')

# grid population
grid_pop = p.Population(n*n, p.IF_curr_exp(**cell_params_lif), label='grid_pop')

p.Projection(inj_pop, grid_pop, p.FromListConnector(injectionConnection),
             p.StaticSynapse(weight=weight_to_spike, delay=5))

# Connectors
#dist_dep_exc = "d<2.5"
#dist_dep_inh = "d<1.5"
#dist_dep_exc = "exp(-d)/{tau_exc}".format(tau_exc=tau_exc)
#dist_dep_inh = 'exp(-0.5*d)/{tau_inh}'.format(tau_inh=tau_inh)

exc_connector_set = csa.disc(2.5)*csa.euclidMetric2d(grid)
exc_connector = p.CSAConnector(exc_connector_set)

#exc_connector = p.DistanceDependentProbabilityConnector(
#    dist_dep_exc, allow_self_connections=False)

inh_connector_set = csa.disc(1.5)*csa.euclidMetric2d(grid)
inh_connector = p.CSAConnector(inh_connector_set)

#inh_connector = p.DistanceDependentProbabilityConnector(
#    dist_dep_inh, allow_self_connections=False)

# Wire grid
p.Projection(grid_pop, grid_pop, exc_connector,
             p.StaticSynapse(weight=2.0, delay=10))
p.Projection(grid_pop, grid_pop, inh_connector,
             p.StaticSynapse(weight=0.5, delay=15))

grid_pop.record(['v','spikes'])

p.run(runtime)

exc_connector.show_connection_set(n*n, n*n)
csa.gplotsel2d(grid, exc_connector_set, range(n*n), range(n*n), N0=n*n)
inh_connector.show_connection_set(n*n, n*n)
csa.gplotsel2d(grid, inh_connector_set, range(n*n), range(n*n), N0=n*n)

v = grid_pop.get_data('v')
spikes = grid_pop.get_data('spikes')

Figure(
    # raster plot of the presynaptic neurons' spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=2.0, xlim=(0, runtime), xticks=True),
    # membrane potential of the postsynaptic neurons
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[grid_pop.label], yticks=True, xlim=(0, runtime),
          xticks=True),
    title="Simple grids from CSA connector",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()