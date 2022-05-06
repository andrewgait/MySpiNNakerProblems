import pyNN.spiNNaker as sim

# test the clear function when using recording

sim.setup(timestep=1.0)

input_pop_size = 100
neuron_pop_size = 60
output_pop_size = 10

input_pop = sim.Population(
    neuron_pop_size, sim.SpikeSourcePoisson(rate=50), label="input")
pop = sim.Population(neuron_pop_size, sim.IF_curr_exp, label="pop2")

out_pop = sim.Population(output_pop_size, sim.IF_curr_exp, label="out_pop")

in_proj = sim.Projection(input_pop, pop, sim.AllToAllConnector(),
                         sim.StaticSynapse(weight=0.2, delay=3))

out_proj = sim.Projection(pop, out_pop, sim.FixedProbabilityConnector(0.5),
                          sim.StaticSynapse(weight=2.0, delay=5))

input_pop.record(['spikes'])
pop.record(['spikes'])
pop.record(['gsyn_exc', 'v', 'gsyn_inh'],
           indexes=[i for i in range(int((neuron_pop_size/2)-5),
                                     int((neuron_pop_size/2)+5))])
out_pop.record(['spikes'])
out_pop.record(['v'], indexes=[3, 4, 5, 6])

for i in range(20):
    print("run ", i)
    sim.run(10000)

    spikes = pop.get_data('spikes', clear=True)
    spikes_out = out_pop.get_data('spikes', clear=True)
    v_pop = pop.get_data('v', clear=True)
    gsyn_e_pop = pop.get_data('gsyn_exc', clear=True)
    gsyn_i_pop = pop.get_data('gsyn_inh', clear=True)
    v_out = out_pop.get_data('v', clear=True)

    print(spikes.segments[0].spiketrains)
    print(v_pop.segments[0].filter(name='v')[0])
    print(gsyn_e_pop.segments[0].filter(name='gsyn_exc')[0])
    print(gsyn_i_pop.segments[0].filter(name='gsyn_inh')[0])
    print(spikes_out.segments[0].spiketrains)
    print(v_out.segments[0].filter(name='v')[0])


sim.end()
