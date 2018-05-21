import spynnaker8 as p

p.setup(timestep=1.0)

inp = p.Population(1, p.SpikeSourceArray(spike_times=[0]))
out = p.Population(1, p.IF_curr_exp())

connector = p.OneToOneConnector()

proj_1 = p.Projection(inp, out, connector,
                      p.StaticSynapse(weight=2.0, delay=17.0))

p.run(1)

print proj_1.get(("weight", "delay"), "list")

p.end()