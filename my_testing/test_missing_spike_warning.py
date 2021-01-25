import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=0.1)
run_1 = 30
run_2 = 25
runtime = run_1 + run_2
print("get_current_time", sim.get_current_time())
pop_1 = sim.Population(1, sim.IF_curr_exp(), label="pop_1")
pop_2 = sim.Population(1, sim.SpikeSourceArray([1, 25]))

proj_1 = sim.Projection(pop_2, pop_1, sim.OneToOneConnector(),
                        synapse_type=sim.StaticSynapse(weight=5.0))

pop_1.record('all')

sim.run(run_1)

pop_2.set(spike_times=[26, 30, 40, 800])

sim.run(run_2)

v = pop_1.get_data('v')
gsyn_exc = pop_1.get_data('gsyn_exc')
gsyn_inh = pop_1.get_data('gsyn_inh')
spikes = pop_1.get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()
