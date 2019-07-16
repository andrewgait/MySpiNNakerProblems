import spynnaker8 as sim

sim.setup(1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 2)
pop = sim.Population(6, sim.IF_curr_exp(i_offset=1, tau_syn_E=1), label="pop")

pop.record("v")
pop.initialize(v=-60)
sim.run(3)
pop.set(tau_syn_E=1)
sim.run(2)
neo = pop.get_data("v")
v = neo.segments[0].filter(name="v")
print(v)

sim.end()