import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

n1 = 6
n2 = 6
runtime = 100
sim.set_number_of_neurons_per_core(sim.IF_curr_exp(), 2)

pop1 = sim.Population(n1, sim.IF_curr_exp(), label="pop1")
pop2 = sim.Population(n2, sim.IF_curr_exp(), label="pop2")

weights = 1.0
delays = 1.0

# proj1 = sim.Projection(pop1, pop2, sim.OneToOneConnector(),
#                        sim.StaticSynapse(weight=weights, delay=delays))
proj2 = sim.Projection(pop1[0:4], pop2[2:6], sim.OneToOneConnector(),
                       sim.StaticSynapse(weight=weights, delay=delays))

sim.run(runtime)

# print(proj1.get(['weight', 'delay'], 'list'))
print(proj2.get(['weight', 'delay'], 'list'))

sim.end()
