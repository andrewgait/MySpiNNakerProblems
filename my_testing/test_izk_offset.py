import spynnaker8 as p

n_neurons = 1
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)

cell_params_izk2 = {'a': 0.02,
                    'b': 0.2,
                    'c': -65,
                    'd': 8,
                    'v': -75,
                    'u': 0,
                    'tau_syn_E': 2,
                    'tau_syn_I': 2,
                    'i_offset': 2
                    }

cell_params_izk4 = {'a': 0.02,
                    'b': 0.2,
                    'c': -65,
                    'd': 8,
                    'v': -75,
                    'u': 0,
                    'tau_syn_E': 2,
                    'tau_syn_I': 2,
                    'i_offset': 4
                    }

populations = list()
populations.append(p.Population(n_neurons, p.Izhikevich, cell_params_izk2,
                                label='pop_1'))
populations.append(p.Population(n_neurons, p.Izhikevich, cell_params_izk4,
                                label='pop_1'))
populations[0].record(["spikes", "v"])
populations[1].record(["spikes", "v"])
p.run(1000)

neo_spikes2 = populations[0].get_data("spikes")
neo_v2 = populations[0].get_data("v")
neo_spikes4 = populations[1].get_data("spikes")
neo_v4 = populations[1].get_data("v")

print(neo_spikes2.segments[0].spiketrains)
print(neo_v2.segments[0].filter(name='v')[0])
print(neo_spikes4.segments[0].spiketrains)
print(neo_v4.segments[0].filter(name='v')[0])

p.end()