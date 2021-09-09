import spynnaker8 as p
import numpy

p.setup(1)
simtime = 100
# starttime = p.RandomDistribution('uniform', (500, 700), rng=p.NumpyRNG(seed=85524))
rng = numpy.random.default_rng(85524)
starttime = rng.integers(low=500, high=700)
print(starttime)
# starttime = 500
pop_src = p.Population(1, p.SpikeSourcePoisson(
    rate=50, start=starttime, duration=simtime), label="src")
pop_src.record("spikes")

p.run(2000)

# for i in range(simtime//2):
#     p.run(2)

spikes = pop_src.get_data("spikes")
p.end()
print(spikes.segments[0].spiketrains)
