import numpy as np
import spynnaker8 as sim

n_neurons = 10
weights = 0.5
delays = 7

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

# p1view = p1[2:8]
# p2view = p2[4:7]

n_pre = 2
# n_pre = sim.RandomDistribution('uniform', [2, 5])

connector_pre = sim.FixedNumberPreConnector(n_pre) # n_neurons+2,
#                                             with_replacement=True)

# proj_pre = sim.Projection(p1view, p2view, connector_pre,
proj_pre = sim.Projection(p1, p2, connector_pre,
                          synapse_type=sim.StaticSynapse(
                              weight=weights, delay=delays))

sim.run(10)

weights_delays_pre = proj_pre.get(["weight", "delay"], "list")
print('fixedpre: ', sorted(weights_delays_pre, key = lambda x: x[1]))

print('unsorted: ', list(weights_delays_pre))

sim.end()

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

p11 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p22 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

print("weights_delays_pre now: ", weights_delays_pre)
# weights_delays_list = [(0,0,1,1), (1,1,2,2), (2,2,3,3)]
weights_delays_list = weights_delays_pre
# weights_delays_list = []
# for n in range(len(weights_delays_pre)):
#     elem_arr = (weights_delays_pre[n][0], weights_delays_pre[n][1],
#                 weights_delays_pre[n][2], weights_delays_pre[n][3])
#     weights_delays_list.append(elem_arr)

fromlist_conn = sim.FromListConnector(weights_delays_list)

proj_new = sim.Projection(p11, p22, fromlist_conn)

sim.run(10)

weights_delays_out = proj_new.get(["weight", "delay"], "list")

print("original weights (first experiment) ", sorted(weights_delays_pre, key = lambda x: x[1]))
print("new weights (second experiment) ", sorted(weights_delays_out, key = lambda x: x[1]))

sim.end()

print("weights_delays_list shape ", np.array(weights_delays_list).shape)
print("weights_delays_pre shape ", np.array(weights_delays_pre).shape)
print("weights_delays_out shape ", np.array(weights_delays_out).shape)
