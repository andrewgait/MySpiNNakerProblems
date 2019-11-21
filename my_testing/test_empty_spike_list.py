# test weirdness with end / import ... and empty lists to SSAs
import spynnaker8 as sim
import numpy

def run_script(simtime):

    sim.setup(timestep=1.0)
    sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 2)
    spike_times = [[1], [], [], [], [4], [3]]
    # spike_times = [[], [], []]
    input1 = sim.Population(
        6, sim.SpikeSourceArray(spike_times=spike_times), label="input1")
    input1.record("spikes")
    sim.run(simtime)

    neo = input1.get_data(variables=["spikes"])
    spikes = neo.segments[0].spiketrains
    print(spikes)

    spikes_test = [list(spikes[i].times.magnitude) for i in range(len(spikes))]
    print(spikes_test)

    # s_spikes = input1.spinnaker_get_data('spikes')
    # print(s_spikes)
    #
    # boxed_array = numpy.zeros(shape=(0, 2))
    # boxed_array = numpy.append(boxed_array, [[0, 0]], axis=0)
    # print(boxed_array)

    # numpy.testing.assert_array_equal(s_spikes, boxed_array)

    numpy.testing.assert_array_equal(spikes_test, spike_times)

    sim.end()

simtime = 5000
for _ in range(10):
    run_script(simtime)
