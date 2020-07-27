import numpy as np
import spynnaker8 as p

# x_res = 304
# y_res = 240
x_res = 5
y_res = 5

shape_pre = np.asarray([x_res, y_res])
# shape_pre = np.asarray([2,2])
# shape_kernel = np.asarray([100, 100])
shape_kernel = np.asarray([3, 3])
# overlap = 0.4
# pre_sample_steps = shape_kernel * (1.0 - overlap)
pre_sample_steps = np.asarray([4, 4])
# post_sample_steps = np.asarray([4, 4])
start_location = np.asarray([0, 0])
# start_location = np.asarray((shape_kernel/2).astype(int))
# shape_post = np.asarray([int((x_res - shape_kernel[0]) / pre_sample_steps[0]) + 1,
#                          int((y_res - shape_kernel[1]) / pre_sample_steps[1]) + 1])
# post_sample_steps = shape_kernel * (1.0 - overlap)
post_sample_steps = np.asarray([1, 1])
shape_post = np.asarray([2, 2])
# shape_post = shape_pre

# kernels = [np.clip(np.random.rand(*shape_kernel), a_min=0, a_max=None) for i in range(1)]
kernels = [[[(a+1)*0.1 + (b+1)*1.0 for a in range(3)] for b in range(3)]]

print("shape_pre", shape_pre)
print("shape_post", shape_post)
print("shape_kernel", shape_kernel)
print("pre_sample_steps", pre_sample_steps)
print("post_sample_steps", post_sample_steps)
# print("start_location", start_location)
print("n_kernels", len(kernels))

p.setup(timestep=1)
# p.set_number_of_neurons_per_core(p.IF_curr_exp, 64)
# p.set_number_of_neurons_per_core(p.SpikeSourceArray, 64)

spike_times = [[i] for i in range(int(x_res*y_res))]

pre_pop = p.Population(x_res*y_res, p.SpikeSourceArray(spike_times=spike_times))

# pre_pop2 = p.Population(x_res*y_res//2, p.SpikeSourceArray(spike_times=spike_times))


post_pop = p.Population(shape_post[0]*shape_post[1], p.IF_curr_exp())

def make_projection(kernel):
    print('weight_kernel: ', kernel)
    return p.Projection(pre_pop, post_pop,
                        p.KernelConnector(shape_pre=shape_pre,
                                          shape_post=shape_post,
                                          shape_kernel=shape_kernel,
                                          weight_kernel=kernel,
                                          post_sample_steps_in_pre=pre_sample_steps,
                                          pre_sample_steps_in_post=post_sample_steps,
                                          post_start_coords_in_pre=start_location,
                                          pre_start_coords_in_post=start_location),
                        receptor_type='excitatory')
#     return p.Projection(pre_pop, post_pop,
#                         p.AllToAllConnector(),
#                         p.StaticSynapse(weight=1.0, delay=1),
#                         receptor_type='excitatory')


# projections = [make_projection(kernel) for kernel in kernels]
projections = [make_projection(np.asarray(kernel)) for kernel in kernels]

runtime = x_res*y_res
p.run(runtime)

conn_data = projections[0].get(["weight", "delay"], "list")
# conn_data2 = projections[1].get(["weight", "delay"], "list")

print(len(conn_data), conn_data)
# print(len(conn_data2), conn_data2)

p.end()
