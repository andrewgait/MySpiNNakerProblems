import spynnaker8 as p

print(round(0.5))

p.setup(timestep=1.0)
#p.setup()
#spikeArray = {'spike_times': [[0]]}
inp = p.Population(1, p.SpikeSourceArray(spike_times=[0]))
out = p.Population(1, p.IF_curr_exp())

connector = p.OneToOneConnector()

proj_1 = p.Projection(inp, out, connector,
                      p.StaticSynapse(weight=2.0, delay=2.0))
#proj_1.set_weights_and_delays(weight=2.0, delay=2.0)
proj_2 = p.Projection(inp, out, connector,
                      p.StaticSynapse(weight=1.0, delay=1.0))

p.run(1)

print(proj_1.get(("weight", "delay"), "list"))
print(proj_2.get(("weight", "delay"), "list"))

p.end()