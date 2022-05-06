import pyNN.spiNNaker as p

print(round(0.5))

p.setup(timestep=1.0)
#p.setup()
#spikeArray = {'spike_times': [[0]]}
inp1 = p.Population(10, p.SpikeSourceArray(spike_times=[0]))
out1 = p.Population(10, p.IF_curr_exp())
inp2 = p.Population(5, p.SpikeSourceArray(spike_times=[0]))
out2 = p.Population(5, p.IF_curr_exp())

# p.set_number_of_neurons_per_core(p.IF_curr_exp(), 50)

connector = p.AllToAllConnector()

proj_1 = p.Projection(inp1, out1, connector,
                      p.StaticSynapse(weight=2.0, delay=4.0))
#proj_1.set_weights_and_delays(weight=2.0, delay=2.0)
proj_2 = p.Projection(inp2, out2, connector,
                      p.StaticSynapse(weight=1.0, delay=11.0))

p.run(1)

print(proj_1.get(("weight", "delay"), "list"))
print(proj_2.get(("weight", "delay"), "list"))

p.end()