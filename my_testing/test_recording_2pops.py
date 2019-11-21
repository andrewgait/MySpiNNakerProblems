import spynnaker8 as sim

sim.setup(timestep=1.0)

pop1 = sim.Population(1, sim.IF_curr_exp, label="pop1")
pop2 = sim.Population(1, sim.IF_curr_exp, label="pop2")

pop1.record('v')
pop2.record('v')
sim.run(1)

v1 = pop1.get_data('v')
v2 = pop2.get_data('v')

sim.end()
