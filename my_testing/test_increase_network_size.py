import spynnaker8 as sim

sim.setup(timestep=1.0, min_delay=1, max_delay=100)

simtime = 1000

n = 100

pop_src = sim.Population(1, sim.SpikeSourcePoisson(rate=10), label="spike_source")
pop_rec = sim.Population(n, sim.IF_cond_exp(), label="test_pop")

weight = 0.01
delay = 2
pconn = 0.5
connector = sim.FixedProbabilityConnector(p_connect=pconn)
synapse = sim.StaticSynapse(weight=weight, delay=delay)

proj = sim.Projection(pop_src, pop_rec, connector, synapse,
                      receptor_type="excitatory")

pop_rec.record('spikes')

sim.run(simtime)

spiketrains = pop_rec.get_data('spikes').segments[0].spiketrains
print("spikes: ", spiketrains[0])

sim.end()






