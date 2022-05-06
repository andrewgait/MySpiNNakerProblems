import matplotlib.pyplot as pylab
import statistics
import math
import pyNN.spiNNaker as sim

rates = [400, 800, 1200]

n_neurons = 128 # 20 # number of neurons in each population
# tstep = 0.1
tstep = 1.0
simtime = 0.001 * 1000 * tstep

sim.setup(timestep=tstep, min_delay=1.0*tstep, max_delay=144.0*tstep)
# sim.setup(timestep=0.1, min_delay=0.1, max_delay=14.4)
sim.set_number_of_neurons_per_core(sim.PoissonSource, 64)

rng = sim.NumpyRNG(seed=1)

weights = sim.RandomDistribution('uniform', [1.0, 3.0], rng=rng)

inputs = {}
for rate in rates:
    params = {"rate": rate, "poisson_weight": weights}
    input = sim.Population(
        n_neurons, sim.PoissonSource, params, label='inputSpikes_'+str(rate))
#     input.record("spikes")  # no recording on this population yet
    inputs[rate] = input

sim.run(simtime)

print('inputs: ', inputs)

sim.end()

# recording has been turned off for PoissonSource so the rest of this script
# won't work at the moment
#
# means = {}
# vars = {}
# with open("spikes2.csv", "w") as spike_file:
#     for rate in rates:
#         neo = inputs[rate].get_data("spikes")
#         spikes = neo.segments[0].spiketrains
#         counts = []
#         spike_file.write(str(rate))
#         for a_spikes in spikes:
#             spike_file.write(",")
#             length = len(a_spikes)
#             spike_file.write(str(length))
#             counts.append(length)
#         spike_file.write("\n")
#         means[rate] = statistics.mean(counts)
#         vars[rate] = statistics.variance(counts, means[rate])
#
# sim.end()
#
# means_plot = []
# vars_plot = []
# means_log_plot = []
# vars_log_plot = []
# for rate in rates:
#     print(rate, means[rate], vars[rate])
#     means_plot.append(means[rate])
#     vars_plot.append(vars[rate])
#     means_log_plot.append(math.log(means[rate]) if means[rate]!=0 else 0)
#     vars_log_plot.append(math.log(vars[rate]) if vars[rate]!=0 else 0)
#
# # plot means against variances
# low = 14
# pylab.subplot(2, 2, 1)
# pylab.xlabel("Means")
# pylab.ylabel("Variances")
# pylab.title("mean vs variance, all")
# pylab.plot(means_plot, vars_plot, 'ro-')
#
# pylab.subplot(2, 2, 2)
# pylab.xlabel("Means")
# pylab.ylabel("Variances")
# pylab.title("low end values")
# pylab.plot(means_plot[0:low], vars_plot[0:low], 'ro-')
#
# pylab.subplot(2, 2, 3)
# pylab.xlabel("Means")
# pylab.ylabel("Variances")
# pylab.title("log, mean vs variance, all")
# pylab.plot(means_log_plot, vars_log_plot, 'bo')
#
# pylab.subplot(2, 2, 4)
# pylab.xlabel("Means")
# pylab.ylabel("Variances")
# pylab.title("log, low end values")
# pylab.plot(means_log_plot[0:low], vars_log_plot[0:low], 'bo')
#
# pylab.subplots_adjust(wspace=0.5, hspace=0.5)
#
# pylab.show()