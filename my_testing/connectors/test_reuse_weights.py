import spynnaker8 as sim

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

n_neurons = 10
weights = 0.5
delays = 7
n_pre = 2

p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1_1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1_2')

connector_pre = sim.FixedNumberPreConnector(n_pre)

proj_pre = sim.Projection(p1, p2, connector_pre,
                          synapse_type=sim.StaticSynapse(
                              weight=weights, delay=delays))

sim.run(10)

weights_delays_pre = proj_pre.get(["weight", "delay"], "list")

sim.end()

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

p11 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2_1')
p22 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2_2')

fromlist_conn = sim.FromListConnector(weights_delays_pre)

proj_new = sim.Projection(p11, p22, fromlist_conn)

sim.run(10)

weights_delays_out = proj_new.get(["weight", "delay"], "list")

sim.end()

print("weights_delays_pre ", dir(weights_delays_pre))
print("weights_delays_out ", dir(weights_delays_out))

print(weights_delays_pre == weights_delays_out)

for n in range(len(weights_delays_pre)):
    print(weights_delays_pre[n], weights_delays_out[n])
    print(weights_delays_pre[n] == weights_delays_out[n])
