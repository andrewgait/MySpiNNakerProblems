import pyNN.spiNNaker as sim

sim.setup(timestep=1)

pop_1 = sim.Population(5, sim.IF_curr_exp(), label="pop_1")
simtime = 10
sim.run(simtime)

sim.reset()

pop_2 = sim.Population(5, sim.IF_curr_exp(), label="pop_2")
sim.run(simtime)

sim.end()