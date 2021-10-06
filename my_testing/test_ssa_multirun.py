import spynnaker8 as sim
sim.setup(timestep=1.0)
input = sim.Population(1, sim.SpikeSourceArray(spike_times=[1, 12, 23]), label="input")
input.record("spikes")
sim.run(10)
sim.run(10)