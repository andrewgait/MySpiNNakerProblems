import pyNN.spiNNaker as sim
import numpy as np
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

# pre and post shape
psh = 36
psw = 36
n_pop = psw*psh
runtime = (n_pop*5)+1000

spiking = [[n*5, (n_pop*5)-1-(n*5)] for n in range(n_pop)]
# spiking = [[n*5, ((n_pop//4)*5)-1-(n*5)] for n in range(n_pop // 4)]
print('ssa using ', spiking)

# input_pop = sim.Population(n_pop // 4, sim.SpikeSourceArray(spiking), label="input")
# pop = sim.Population(n_pop, sim.IF_curr_exp(), label="pop")
input_pop = sim.Population(n_pop, sim.SpikeSourceArray(spiking), label="input")
pop = sim.Population(n_pop // 4, sim.IF_curr_exp(), label="pop")

weights = 5.0
delays = 17.0

ksh = 4
ksw = 2
pre_start_in_post = [0, 0]
post_start_in_pre = [2, 1]
pre_step_in_post = [1, 1]
post_step_in_pre = [2, 1]

shape_pre = [psh, psw]
shape_post = [psh // 2, psw // 2]
# shape_pre = [psh // 2, psw // 2]
# shape_post = [psh, psw]
shape_kernel = [ksh, ksw]
# weight_list = [[(a+1)*2.0 + (b+1)*1.0 for a in range(ks)] for b in range(ks)]
weight_list = [[2.5 if (a == 2) or (b == 2) else 0.0 for a in range(ksw)] for b in range(ksh)]
# delay_list = [[(a+1)*1.0 + (b+1)*2.0 for a in range(ks)] for b in range(ks)]
delay_list = [[10.0 if (a == 2) or (b == 2) else 1.0 for a in range(ksw)] for b in range(ksh)]
print('weight_list', weight_list)
print('delay_list', delay_list)
weight_kernel = np.asarray(weight_list)
delay_kernel = np.asarray(delay_list)
# pre_step = [2, 2]
# post_step = [2, 2]
kernel_connector = sim.KernelConnector(shape_pre, shape_post, shape_kernel,
#                                        shape_common=shape_post,
                                       weight_kernel=weight_kernel,
                                       delay_kernel=delay_kernel,
                                       pre_sample_steps_in_post=pre_step_in_post,
                                       pre_start_coords_in_post=pre_start_in_post,
                                       post_sample_steps_in_pre=post_step_in_pre,
                                       post_start_coords_in_pre=post_start_in_pre)
print('kernel connector is: ', kernel_connector)
c2 = sim.Projection(input_pop, pop, kernel_connector,
                    sim.StaticSynapse(weight=weights, delay=delays))

pop.record(['v', 'spikes'])

sim.run(runtime)

weightsdelays = sorted(c2.get(['weight', 'delay'], 'list'),
                       key = lambda x: x[1])
print(weightsdelays)
print('there are', len(weightsdelays), 'connections')

# get data (could be done as one, but can be done bit by bit as well)
spikes = pop.get_data('spikes')
v = pop.get_data('v')

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, runtime)),
    title="kernel connector testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

plt.xlabel("pre")
plt.ylabel("post")
plt.title("n_pre={}, n_post={}, without replacement, no self-conn".format(
    n_pop, n_pop // 4))
plt.plot(list(weightsdelays[n][0] for n in range(len(weightsdelays))),
         list(weightsdelays[n][1] for n in range(len(weightsdelays))),
         'ro', markersize=0.5)

plt.show()

sim.end()
