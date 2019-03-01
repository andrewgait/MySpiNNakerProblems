import spynnaker8 as sim

sim.setup(1.0)
pop = sim.Population(1, sim.IF_curr_exp, {}, label="pop")
pop.set(i_offset=1.0)
pop.record(["v"])

pop.initialize(v=-62.0)
pop.set(tau_syn_E=1)
sim.run(5)

pop.initialize(v=-63.0)
pop.set(tau_syn_E=1)
sim.run(5)
v1 = pop.spinnaker_get_data('v')

sim.reset()
pop.initialize(v=-64.0)
pop.set(tau_syn_E=1)
sim.run(5)

pop.initialize(v=-61.0)
pop.set(tau_syn_E=1)
sim.run(5)
v2 = pop.spinnaker_get_data('v')

sim.end()

print(v1)
print(v2)