# import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np

def test_levels(rates=(150, 125, 100), weights=(0.01, 0.015)):
    counter = 0
    receive_pop = []
    spike_input = []
    p.setup(timestep=1, min_delay=1, max_delay=127)
    p.set_number_of_neurons_per_core(p.IF_cond_exp, 10)
    for rate in rates:
        for weight in weights:
            pop_size = 10
            receive_pop.append(p.Population(pop_size, p.IF_cond_exp()))#, label="receive_pop{}-{}".format(rate, weight)))

            receive_pop[counter].record(['spikes', 'v'])#["spikes"])

            # Connect key spike injector to input population
            spike_input.append(p.Population(pop_size, p.SpikeSourcePoisson(rate=rate), label="input_connect{}-{}".format(rate, weight)))
            p.Projection(
                spike_input[counter], receive_pop[counter], p.OneToOneConnector(), p.StaticSynapse(weight=weight))

            print("reached here 1")
            runtime = 11000

            counter += 1

    p.run(runtime)
    print("reached here 2")

    for i in range(counter):
        weight_index = i % len(weights)
        rate_index = (i - weight_index) / len(weights)
        print(weight_index)
        print(rate_index)
        # for j in range(receive_pop_size):
        spikes = receive_pop[i].get_data('spikes').segments[0].spiketrains
        v = receive_pop[i].get_data('v').segments[0].filter(name='v')[0]
        plt.figure("rate = {} - weight = {}".format(rates[rate_index], weights[weight_index]))
        Figure(
            Panel(spikes, xlabel="Time (ms)", ylabel="nID", xticks=True),
            Panel(v, ylabel="Membrane potential (mV)", yticks=True)
        )
        plt.show()

    # End simulation
    p.end()

def test_packets(rate=100, weight=0.01, probability=0.7, seed=27,
                 pop_size=2, count=200, with_bandit=False):
    import spynnaker8 as p
    counter = 0
    receive_pop = []
    output_pop = []
    spike_input = []
    bandit_pops = []
    p.setup(timestep=1.0, min_delay=1, max_delay=127)
    p.set_number_of_neurons_per_core(p.IF_curr_exp, 10)
    for i in range(count):
        # pop_size = 2

        receive_pop.append(p.Population(pop_size, p.IF_curr_exp(),
                                        label="receive_pop{}".format(i)))
        output_pop.append(p.Population(2, p.IF_curr_exp(),
                                       label="output_pop{}".format(i)))
        p.Projection(receive_pop[counter], output_pop[counter],
                     p.AllToAllConnector(), p.StaticSynapse(weight=0.1))
        np.random.seed(seed)

        # next idea: turn off the output population as well?

        p.Projection(receive_pop[counter], receive_pop[counter],
                     p.FixedProbabilityConnector(probability),
                     p.StaticSynapse(weight=0.1))
        p.Projection(output_pop[counter], output_pop[counter],
                     p.FixedProbabilityConnector(probability),
                     p.StaticSynapse(weight=0.1))

        receive_pop[counter].record(['spikes'])#, 'v'])#["spikes"])

        # Connect key spike injector to input population
        spike_input.append(p.Population(
            pop_size, p.SpikeSourcePoisson(rate=rate),
            label="input_connect{}-{}".format(rate, weight)))
        p.Projection(
            spike_input[counter], receive_pop[counter],
            p.OneToOneConnector(), p.StaticSynapse(weight=weight))
        # spike_output.append(p.Population(pop_size, p.SpikeSourcePoisson(rate=rate), label="input_connect{}-{}".format(rate, weight)))
#        p.Projection(
#            spike_input[counter], receive_pop[counter],
#            p.OneToOneConnector(), p.StaticSynapse(weight=weight))

        runtime = 21000

        counter += 1

    p.run(runtime)

    spikes = []
    for i in range(counter):
        spikes.append(
            receive_pop[i].get_data('spikes').segments[0].spiketrains)

    # End simulation
    p.end()
    print("ended")

# test_levels()
for prob in np.linspace(0.5,1.0,10):
    seed = np.random.randint(0,1000)
    print("seed:", seed, "prob:", prob)
    test_packets(probability=prob, seed=seed, count=200, with_bandit=False)
