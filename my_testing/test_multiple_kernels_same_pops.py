import numpy as np
import spynnaker8 as p

x_res = 100.
y_res = 100.

shape_pre = np.asarray([x_res, y_res])
shape_kernel = np.asarray([5, 5])
pre_sample_steps = (1,1)
start_location = np.asarray((shape_kernel/2).astype(int))
shape_post = np.asarray([int((x_res - shape_kernel[0]) / pre_sample_steps[0]) + 1,
                         int((y_res - shape_kernel[1]) / pre_sample_steps[1]) + 1])

kernels = [np.clip(np.random.rand(*shape_kernel), a_min=0, a_max=None) for i in range(24)]


print("shape_pre", shape_pre)
print("shape_post", shape_post)
print("shape_kernel", shape_kernel)
print("pre_sample_steps", pre_sample_steps)
print("start_location", start_location)

p.setup(timestep=1)
p.set_number_of_neurons_per_core(p.IF_curr_exp, 16)
p.set_number_of_neurons_per_core(p.SpikeSourceArray, 16)


spike_times = [[i] for i in range(int(x_res*y_res))]

pre_pop = p.Population(x_res*y_res, p.SpikeSourceArray(spike_times=spike_times))

post_pop = p.Population(shape_post[0]*shape_post[1], p.IF_curr_exp())

def make_projection(kernel):
    print('weight_kernel: ', kernel)
    return p.Projection(pre_pop, post_pop,
                        p.KernelConnector(shape_pre=shape_pre,
                                          shape_post=shape_post,
                                          shape_kernel=shape_kernel,
                                          weight_kernel=kernel,
                                          post_sample_steps_in_pre=pre_sample_steps,
                                          post_start_coords_in_pre=start_location),
                        receptor_type='excitatory')


projections = [make_projection(kernel) for kernel in kernels]

runtime = x_res*y_res
p.run(runtime)

p.end()
