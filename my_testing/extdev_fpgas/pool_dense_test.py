import numpy
import pyNN.spiNNaker as sim
from pyNN.space import Grid2D

numpy.random.seed(13)


shape = numpy.array([5, 5])
n_input = numpy.prod(shape)

vline = [[20. + idx // shape[1]]
         if (idx % shape[1]) == (shape[1] // 2) else []
         for idx in range(n_input)]

vline0 = [[10. + idx // shape[1]]
          if (idx % shape[1]) == (shape[1] // 2) else []
          for idx in range(n_input)]

run_time = 60.

sim.setup(timestep=1.)
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, (3, 3))
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 16)

src = sim.Population(n_input, sim.SpikeSourceArray,
                     {'spike_times': vline},
                     label='input spikes 0',
                     structure=Grid2D(shape[0] / shape[1]))

src1 = sim.Population(n_input, sim.SpikeSourceArray,
                      {'spike_times': vline0},
                      label='input spikes 1',
                      structure=Grid2D(shape[0] / shape[1]))

pooling = numpy.array([2, 2])
post_pool_shape = sim.PoolDenseConnector.get_post_pool_shape(shape, pooling)
n_out = 23
k_shape = numpy.asarray((int(numpy.prod(post_pool_shape)), n_out), dtype='int')

ws = numpy.arange(int(numpy.prod(k_shape))).reshape(k_shape) * 0.01
print(ws.shape)
print(len(ws))
print(ws)

conn = sim.PoolDenseConnector(ws, pooling)
conn1 = sim.PoolDenseConnector(ws - 1.0, pooling)

post_cfg = {
    'v_thresh': 5.,
    'v_reset': 0.,
    'v': 0.,
    'v_rest': 0.,
    'tau_syn_E': 1.0,
    'tau_syn_I': 1.0,
    'tau_m': 1.0
}

dst = sim.Population(n_out, sim.IF_curr_exp, post_cfg)
dst.record(['v', 'spikes'])

prj = sim.Projection(src, dst, conn, sim.PoolDense())
prj1 = sim.Projection(src1, dst, conn1, sim.PoolDense())

sim.run(run_time)

neo = dst.get_data()
v = neo.segments[0].filter(name='v')[0]
spikes = neo.segments[0].spiketrains

sim.end()

print(v)
print(spikes)
