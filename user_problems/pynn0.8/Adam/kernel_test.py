# import matplotlib
# matplotlib.use('Agg')

# import warnings
import numpy as np
import spynnaker8 as p
import matplotlib.pyplot as plt
from pyNN.utility.plotting import Figure, Panel

# warnings.filterwarnings("error")
x_res = 19 #304
y_res = 15 #240
n_kernels = 1 #60
kernel_h = 6
kernel_w = 6

def build_kernel(x_res, y_res, n_kernels, kernel_h, kernel_w):
    shape_pre = np.asarray([x_res, y_res])
    shape_kernel = np.asarray([kernel_h, kernel_w])
    pre_sample_steps = shape_kernel * (1. - 0.6)
    start_location = np.asarray([kernel_h // 2, kernel_w // 2])
    # shape_post = np.asarray([int((x_res - shape_kernel[0]) / pre_sample_steps[0]) + 1, int((y_res - shape_kernel[1]) / pre_sample_steps[1]) + 1])
    shape_post = np.asarray([2, 2])
    weight_kernel = []
    for i in range(int(shape_kernel[0])):
        weight_row = []
        for j in range(int(shape_kernel[1])):
            x_value = ((float(shape_kernel[0]) / 2.) - np.abs(
                i - (float(shape_kernel[0]) / 2.))) / (float(shape_kernel[0]) / 2.)
            y_value = ((float(shape_kernel[1]) / 2.) - np.abs(
                j - (float(shape_kernel[1]) / 2.))) / (float(shape_kernel[1]) / 2.)
            weight_row.append(x_value * y_value)
        weight_kernel.append(weight_row)
    weight_kernel = np.asarray(weight_kernel)

    print("shape_pre", shape_pre)
    print("shape_post", shape_post)
    print("shape_kernel", shape_kernel)
    print("pre_sample_steps", pre_sample_steps)
    print("start_location", start_location)
    print("weight_kernel", weight_kernel)

    print("n_kernels: ", n_kernels)

    post_pops = []

    projs = []

    for n in range(n_kernels):
        post_pops.append(p.Population(int(shape_post[0]*shape_post[1]), p.IF_curr_exp()))
        post_pops[n].record('all')
        projs.append(p.Projection(pre_pop, post_pops[n], p.KernelConnector(
            shape_pre=shape_pre, shape_post=shape_post, shape_kernel=shape_kernel,
            weight_kernel=weight_kernel, post_sample_steps_in_pre=pre_sample_steps,
            post_start_coords_in_pre=start_location)))
    #     p.Projection(pre_pop, post_pop2, p.KernelConnector(
    #         shape_pre=shape_pre, shape_post=shape_post, shape_kernel=shape_kernel,
    #         weight_kernel=weight_kernel, post_sample_steps_in_pre=pre_sample_steps,
    #         post_start_coords_in_pre=start_location))

    return post_pops, projs


def build_fromlist(x_res, y_res, n_kernels):
    # look at how Adam has done this
    post_pops = []
    projs = []
    shape_post = np.asarray([2, 2])

    connections = [(  0, 0, 0.        , 1.), (  1, 0, 0.        , 1.),
                 (  2, 0, 0.        , 1.), (  2, 1, 0.        , 1.),
                 (  3, 0, 0.        , 1.), (  3, 1, 0.        , 1.),
                 (  4, 0, 0.        , 1.), (  4, 1, 0.        , 1.),
                 (  5, 0, 0.        , 1.), (  5, 1, 0.        , 1.),
                 (  6, 1, 0.        , 1.), (  7, 1, 0.        , 1.),
                 ( 15, 0, 0.        , 1.), ( 16, 0, 0.109375  , 1.),
                 ( 17, 0, 0.22070312, 1.), ( 17, 1, 0.        , 1.),
                 ( 18, 0, 0.33203125, 1.), ( 18, 1, 0.109375  , 1.),
                 ( 19, 0, 0.22070312, 1.), ( 19, 1, 0.22070312, 1.),
                 ( 20, 0, 0.109375  , 1.), ( 20, 1, 0.33203125, 1.),
                 ( 21, 1, 0.22070312, 1.), ( 22, 1, 0.109375  , 1.),
                 ( 30, 0, 0.        , 1.), ( 30, 2, 0.        , 1.),
                 ( 31, 0, 0.22070312, 1.), ( 31, 2, 0.        , 1.),
                 ( 32, 0, 0.44335938, 1.), ( 32, 1, 0.        , 1.),
                 ( 32, 2, 0.        , 1.), ( 32, 3, 0.        , 1.),
                 ( 33, 0, 0.66601562, 1.), ( 33, 1, 0.22070312, 1.),
                 ( 33, 2, 0.        , 1.), ( 33, 3, 0.        , 1.),
                 ( 34, 0, 0.44335938, 1.), ( 34, 1, 0.44335938, 1.),
                 ( 34, 2, 0.        , 1.), ( 34, 3, 0.        , 1.),
                 ( 35, 0, 0.22070312, 1.), ( 35, 1, 0.66601562, 1.),
                 ( 35, 2, 0.        , 1.), ( 35, 3, 0.        , 1.),
                 ( 36, 1, 0.44335938, 1.), ( 36, 3, 0.        , 1.),
                 ( 37, 1, 0.22070312, 1.), ( 37, 3, 0.        , 1.),
                 ( 45, 0, 0.        , 1.), ( 45, 2, 0.        , 1.),
                 ( 46, 0, 0.33203125, 1.), ( 46, 2, 0.109375  , 1.),
                 ( 47, 0, 0.66601562, 1.), ( 47, 1, 0.        , 1.),
                 ( 47, 2, 0.22070312, 1.), ( 47, 3, 0.        , 1.),
                 ( 48, 0, 1.        , 1.), ( 48, 1, 0.33203125, 1.),
                 ( 48, 2, 0.33203125, 1.), ( 48, 3, 0.109375  , 1.),
                 ( 49, 0, 0.66601562, 1.), ( 49, 1, 0.66601562, 1.),
                 ( 49, 2, 0.22070312, 1.), ( 49, 3, 0.22070312, 1.),
                 ( 50, 0, 0.33203125, 1.), ( 50, 1, 1.        , 1.),
                 ( 50, 2, 0.109375  , 1.), ( 50, 3, 0.33203125, 1.),
                 ( 51, 1, 0.66601562, 1.), ( 51, 3, 0.22070312, 1.),
                 ( 52, 1, 0.33203125, 1.), ( 52, 3, 0.109375  , 1.),
                 ( 60, 0, 0.        , 1.), ( 60, 2, 0.        , 1.),
                 ( 61, 0, 0.22070312, 1.), ( 61, 2, 0.22070312, 1.),
                 ( 62, 0, 0.44335938, 1.), ( 62, 1, 0.        , 1.),
                 ( 62, 2, 0.44335938, 1.), ( 62, 3, 0.        , 1.),
                 ( 63, 0, 0.66601562, 1.), ( 63, 1, 0.22070312, 1.),
                 ( 63, 2, 0.66601562, 1.), ( 63, 3, 0.22070312, 1.),
                 ( 64, 0, 0.44335938, 1.), ( 64, 1, 0.44335938, 1.),
                 ( 64, 2, 0.44335938, 1.), ( 64, 3, 0.44335938, 1.),
                 ( 65, 0, 0.22070312, 1.), ( 65, 1, 0.66601562, 1.),
                 ( 65, 2, 0.22070312, 1.), ( 65, 3, 0.66601562, 1.),
                 ( 66, 1, 0.44335938, 1.), ( 66, 3, 0.44335938, 1.),
                 ( 67, 1, 0.22070312, 1.), ( 67, 3, 0.22070312, 1.),
                 ( 75, 0, 0.        , 1.), ( 75, 2, 0.        , 1.),
                 ( 76, 0, 0.109375  , 1.), ( 76, 2, 0.33203125, 1.),
                 ( 77, 0, 0.22070312, 1.), ( 77, 1, 0.        , 1.),
                 ( 77, 2, 0.66601562, 1.), ( 77, 3, 0.        , 1.),
                 ( 78, 0, 0.33203125, 1.), ( 78, 1, 0.109375  , 1.),
                 ( 78, 2, 1.        , 1.), ( 78, 3, 0.33203125, 1.),
                 ( 79, 0, 0.22070312, 1.), ( 79, 1, 0.22070312, 1.),
                 ( 79, 2, 0.66601562, 1.), ( 79, 3, 0.66601562, 1.),
                 ( 80, 0, 0.109375  , 1.), ( 80, 1, 0.33203125, 1.),
                 ( 80, 2, 0.33203125, 1.), ( 80, 3, 1.        , 1.),
                 ( 81, 1, 0.22070312, 1.), ( 81, 3, 0.66601562, 1.),
                 ( 82, 1, 0.109375  , 1.), ( 82, 3, 0.33203125, 1.),
                 ( 90, 2, 0.        , 1.), ( 91, 2, 0.22070312, 1.),
                 ( 92, 2, 0.44335938, 1.), ( 92, 3, 0.        , 1.),
                 ( 93, 2, 0.66601562, 1.), ( 93, 3, 0.22070312, 1.),
                 ( 94, 2, 0.44335938, 1.), ( 94, 3, 0.44335938, 1.),
                 ( 95, 2, 0.22070312, 1.), ( 95, 3, 0.66601562, 1.),
                 ( 96, 3, 0.44335938, 1.), ( 97, 3, 0.22070312, 1.),
                 (105, 2, 0.        , 1.), (106, 2, 0.109375  , 1.),
                 (107, 2, 0.22070312, 1.), (107, 3, 0.        , 1.),
                 (108, 2, 0.33203125, 1.), (108, 3, 0.109375  , 1.),
                 (109, 2, 0.22070312, 1.), (109, 3, 0.22070312, 1.),
                 (110, 2, 0.109375  , 1.), (110, 3, 0.33203125, 1.),
                 (111, 3, 0.22070312, 1.), (112, 3, 0.109375  , 1.)]

    for n in range(n_kernels):
        post_pops.append(p.Population(int(shape_post[0]*shape_post[1]), p.IF_curr_exp()))
        post_pops[n].record('all')
        projs.append(p.Projection(pre_pop, post_pops[n],
                                  p.FromListConnector(connections)))

    return post_pops, projs


p.setup(timestep=1)
# p.set_number_of_neurons_per_core(p.SpikeSourceArray(), 128)
# p.set_number_of_neurons_per_core(p.IF_curr_exp(), 128)

spike_times = [[i] for i in range(int(x_res*y_res))]
pre_pop = p.Population(x_res*y_res, p.SpikeSourceArray(spike_times=spike_times))
pre_pop.record('all')

# post_pop = p.Population(shape_post[0]*shape_post[1], p.IF_curr_exp())
# post_pop.record('all')
# post_pop2 = p.Population(shape_post[0]*shape_post[1], p.IF_curr_exp())
# post_pop2.record('all')


# post_pops, projs = build_kernel(x_res, y_res, n_kernels, kernel_h, kernel_w)

post_pops, projs = build_fromlist(x_res, y_res, n_kernels)

runtime = x_res*y_res
p.run(runtime)

pre_spikes = pre_pop.get_data('all')
post_spikes = post_pops[0].get_data('all')

weights_delays = projs[0].get(['weight', 'delay'], 'list')

print(weights_delays)

print("creating graph")
Figure(
    Panel(post_spikes.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=post_pops[0].label, yticks=True, xlim=(0, runtime)),
    Panel(post_spikes.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=post_pops[0].label, yticks=True, xlim=(0, runtime)),
    Panel(post_spikes.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=post_pops[0].label, yticks=True, xlim=(0, runtime)),
    Panel(post_spikes.segments[0].spiketrains,
          ylabel="Output Spikes",
          data_labels=post_pops[0].label, yticks=True, xlim=(0, runtime)),
    Panel(pre_spikes.segments[0].spiketrains,
          ylabel="Output Spikes",
          data_labels=pre_pop.label, yticks=True, xlim=(0, runtime)),
    # Panel(pre_spikes.segments[0].spiketrains,
    #       ylabel="Input Spikes",
    #       data_labels=pre_pop.label, yticks=True, xlim=(0, runtime)),
    title="Spike data"
)
plt.show()

p.end()
