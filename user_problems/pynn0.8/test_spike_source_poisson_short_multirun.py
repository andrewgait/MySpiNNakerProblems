import spynnaker8 as p

p.setup(1)
simtime = 100
pop_src = p.Population(1, p.SpikeSourcePoisson(
    rate=50, start=0, duration=simtime), label="src")
pop_src.record("spikes")

for i in range(simtime//2):
    p.run(2)

spikes = pop_src.get_data("spikes")
p.end()
print(spikes.segments[0].spiketrains)
