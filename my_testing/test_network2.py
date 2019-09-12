
#import matplotlib
#matplotlib.use('SVG')
from pyNN.utility.plotting import Figure, Panel

import spynnaker8 as sim
import matplotlib.pyplot as plt
import numpy as np
simtime=1000.7


sim.setup(timestep=1.0,min_delay=1.0,max_delay=4.0)


delta_cell=sim.Population(1,sim.extra_models.IFCurDelta(**{'i_offset':0.1,'tau_refrac':3.0,'v_thresh':-51.0,'v_reset':-70.0}))

spike_source_E=sim.Population(1,sim.SpikeSourcePoisson(rate=10000.0),label='expoisson')
spike_source_I=sim.Population(1,sim.SpikeSourcePoisson(rate=10000.0),label='inpoisson')


delta_cell.record(['spikes', 'v'])

ext_connector=sim.AllToAllConnector()


input_to_E=sim.Projection(spike_source_E,delta_cell,ext_connector,receptor_type='excitatory',synapse_type=sim.StaticSynapse(weight=0.15,delay=1.5))
in_input_to_E=sim.Projection(spike_source_I,delta_cell,ext_connector,receptor_type='inhibitory',synapse_type=sim.StaticSynapse(weight=-0.15,delay=1.5))

sim.run(simtime)

esp=delta_cell.get_data('spikes')
v_esp=delta_cell.get_data('v')


# def plot_spiketrains(segment):
#     for spiketrain in segment.spiketrains:
#         y = np.ones_like(spiketrain) * spiketrain.annotations['source_id']
#         plt.plot(spiketrain, y, '.', ms=1.0, c='k')
#
#
# plt.figure()
# plot_spiketrains(esp.segments[0])
# plt.xlabel('Time (ms)')
# # plt.show()
# plt.savefig('Pyr_spikes_deltamodel_test.png')

print(esp.segments[0].spiketrains)

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(esp.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, simtime), xticks=True),
    # membrane potential of the postsynaptic neuron
    Panel(v_esp.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[delta_cell.label], yticks=True, xlim=(0, simtime)),
    title="toy example",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
# plt.savefig('Pyr_spikes_deltamodel_test.png')


sim.end()
