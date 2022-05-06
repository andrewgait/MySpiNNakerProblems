import pyNN.spiNNaker as p

p.setup(timestep=1.0)

simtime = 300

pop_src2 = p.Population(1, p.SpikeSourcePoisson(rate=10), label="drive")
pop_ex = p.Population(1, p.IF_curr_exp(), label="test")

proj2 = p.Projection(pop_src2,  pop_ex,  p.OneToOneConnector(),
               synapse_type=p.StaticSynapse(weight=2.0),  receptor_type='excitatory')

pop_src2.record(['spikes'])
pop_ex.record('spikes')

p.run(simtime)

pop_ex.get_data('spikes')
pop_src2.get_data('spikes')

p.end()
print("\n job done")