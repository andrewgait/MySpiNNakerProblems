import spynnaker8 as sim

sim.setup(timestep=1.0)

n_pop = 3
runtime = 100

input_pop2 = sim.Population(n_pop, sim.SpikeSourceArray([0]), label="input")
pop = sim.Population(n_pop, sim.IF_curr_exp(), label="pop")

as_list3 = []
weights = []
delays = []
weights.append(0.3)
delays.append(1)
as_list3.append((0,0))
for n in range(n_pop-2):
    weights.append(1.0)
    delays.append(17)
    as_list3.append((n+1,n+1))
weights.append(2.0)
delays.append(34)
as_list3.append((n_pop-1,n_pop-1))

as_list3.append((0,1))
weights.append(3.0)
delays.append(51)
as_list3.append((1,2))
weights.append(2.5)
delays.append(68)

fromlist = sim.FromListConnector(as_list3)

c3 = sim.Projection(input_pop2, pop, fromlist,
#                    sim.StaticSynapse(weight=0.7, delay=33))
                    sim.StaticSynapse(weight=weights, delay=delays))

test_conn_list = fromlist.conn_list
print(test_conn_list)

sim.run(runtime)

print (c3.get(['weight', 'delay'], 'list'))
print (fromlist.conn_list)

print('timestep ', sim.get_time_step())
print(sim.get_min_delay(), sim.get_max_delay(), sim.get_current_time())

sim.end()