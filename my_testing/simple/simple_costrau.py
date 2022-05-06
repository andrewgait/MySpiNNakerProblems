import pyNN.spiNNaker as p

p.setup(timestep=1.0)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 0.0,
                   'tau_syn_E': 0.1,
                   'tau_syn_I': 0.1,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }

pop = p.Population(200, p.IF_cond_exp(**cell_params_lif), label="pop")
spike_times=[]
for i in range(1000):
    spike_times.append(i*100)
input = p.Population(1, p.SpikeSourceArray,
                     {'spike_times': spike_times}, label="input")
proj = p.Projection(input, pop, p.AllToAllConnector(),
                    p.StaticSynapse(weight=3.0, delay=0.0),
                    receptor_type='excitatory')
proj2 = p.Projection(pop, pop, p.AllToAllConnector(),
                     p.StaticSynapse(weight=3.0, delay=0.0),
                     receptor_type='excitatory')
pop.record(["spikes", "v"])
p.run(100000)
p.end()