import matplotlib.pyplot as pylab
import statistics
import math
import spynnaker8 as sim

rates = [0, 0.0001, 0.0005, 0.001, 0.002, 0.005, 0.007, 0.01, 0.02,
         0.03, 0.04, 0.05, 0.07, 0.09, 0.1, 0.11,
         0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.32, 0.64,
         1.28, 2.56, 5.12, 10.24, 20.48, 40.96, 81.92, 163.84, 327.68, 655.36,
         1310.72, 1966.08, 2621.44, 5242.88, 10485.76, 20971.52, 41943.04]

# rates = [2000, 3000]
n_neurons = 20 # number of neurons in each population
# tstep = 0.1
tstep = 1.0
simtime = 100 * 1000 * tstep

sim.setup(timestep=tstep, min_delay=1.0*tstep, max_delay=144.0*tstep)
# sim.setup(timestep=0.1, min_delay=0.1, max_delay=14.4)

inputs = {}
for rate in rates:
    params = {"rate": rate}
    input = sim.Population(
        n_neurons, sim.SpikeSourcePoisson, params, label='inputSpikes_1')
    input.record("spikes")
    inputs[rate] = input

sim.run(simtime)

means = {}
vars = {}
with open("spikes2.csv", "w") as spike_file:
    for rate in rates:
        neo = inputs[rate].get_data("spikes")
        spikes = neo.segments[0].spiketrains
        counts = []
        spike_file.write(str(rate))
        for a_spikes in spikes:
            spike_file.write(",")
            length = len(a_spikes)
            spike_file.write(str(length))
            counts.append(length)
        spike_file.write("\n")
        means[rate] = statistics.mean(counts)
        vars[rate] = statistics.variance(counts, means[rate])

sim.end()

means_plot = []
vars_plot = []
means_log_plot = []
vars_log_plot = []
for rate in rates:
    print(rate, means[rate], vars[rate])
    means_plot.append(means[rate])
    vars_plot.append(vars[rate])
    means_log_plot.append(math.log(means[rate]) if means[rate]!=0 else 0)
    vars_log_plot.append(math.log(vars[rate]) if vars[rate]!=0 else 0)

# plot means against variances
pylab.subplot(2, 2, 1)
pylab.xlabel("Means")
pylab.ylabel("Variances")
pylab.title("mean vs variance, all")
pylab.plot(means_plot, vars_plot, 'ro-')

pylab.subplot(2, 2, 2)
pylab.xlabel("Means")
pylab.ylabel("Variances")
pylab.title("low end values")
pylab.plot(means_plot[0:15], vars_plot[0:15], 'ro-')

pylab.subplot(2, 2, 3)
pylab.xlabel("Means")
pylab.ylabel("Variances")
pylab.title("log, mean vs variance, all")
pylab.plot(means_log_plot, vars_log_plot, 'bo')

pylab.subplot(2, 2, 4)
pylab.xlabel("Means")
pylab.ylabel("Variances")
pylab.title("log, low end values")
pylab.plot(means_log_plot[0:15], vars_log_plot[0:15], 'bo')

pylab.subplots_adjust(wspace=0.5, hspace=0.5)

pylab.show()