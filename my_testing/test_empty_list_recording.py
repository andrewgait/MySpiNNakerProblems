import pyNN.spiNNaker as p
import numpy as np

p.setup(timestep=1.0)
p.set_number_of_neurons_per_core(p.SpikeSourceArray, 2)
spike_times = [[1], [], [], [], [4], [3]]
input1 = p.Population(
    6, p.SpikeSourceArray(spike_times=spike_times), label="input1")
input1.record("spikes")
p.run(50)

neo = input1.get_data(variables=["spikes"])
spikes = neo.segments[0].spiketrains

spikes_test = [list(spikes[i].times.magnitude) for i in range(len(spikes))]
np.testing.assert_array_equal(spikes_test, spike_times)

p.end()