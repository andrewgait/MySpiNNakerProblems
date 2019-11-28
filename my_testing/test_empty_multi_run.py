import spynnaker8 as sim

sim.setup(timestep=1.0)

sim.run(2)

# sim.reset()
# sim.Population(2, sim.IF_curr_exp(), label='test')

sim.run(2)

sim.end()