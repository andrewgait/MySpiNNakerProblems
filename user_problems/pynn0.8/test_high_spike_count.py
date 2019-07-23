import spynnaker8 as p

p.setup(timestep=1)

pop = p.Population(16, p.IF_cond_exp, {'tau_refrac' : 0.0}, label="pop")

# p.set_number_of_neurons_per_core(p.IF_cond_exp, 100)

spike_times=[]
for i in range(1000):
    spike_times.append(i*100)

input = p.Population(1, p.SpikeSourceArray(spike_times),
                     label="input")

proj = p.Projection(input, pop, p.FixedProbabilityConnector(0.75),
                    p.StaticSynapse(weight=2.0, delay=1.0),
                    receptor_type='excitatory')

weightdist = p.RandomDistribution("uniform", [1.0, 4.0])
delaydist = p.RandomDistribution("uniform", [1.0, 100.0])

proj2 = p.Projection(pop, pop, p.FixedProbabilityConnector(0.75),
                     p.StaticSynapse(weight=weightdist, delay=delaydist),
                     receptor_type='excitatory')

pop.record('all')
p.run(10000)

v = pop.get_data('v')
spikes = pop.get_data('spikes')
spikes1 = pop.spinnaker_get_data('spikes')

print('spikes length: ', len(spikes1))

p.end()