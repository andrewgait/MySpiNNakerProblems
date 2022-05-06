import pylab
import os
import numpy
import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 0.1,
                   'tau_syn_I': 0.1,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0,
                   'v': -61.0,
                   }

input = sim.Population(1, sim.SpikeSourceArray([[1]]), label='input')
receiver = sim.Population(2, sim.IF_curr_exp(**cell_params_lif),
                          initial_values={'v': -63.5}, label='receiver')

# receiver.initialize(v=[-65.0,-62.0])

columns = ["delay", "weight"]
connection_list = [
    (0, 0, 1.0, 5.5),
    (0, 1, 2.0, 8.0),
#     (0, 1, 2.0, 8.0),
    (0, 4, 3.0, 4.0)
    ]

conn = sim.FromListConnector(connection_list, column_names=columns)
#conn = sim.FixedTotalNumberConnector(1)
# conn = sim.FromListConnector(connection_list)
# conn = sim.FromListConnector(connections_test)

# Here I am testing that these don't overwrite the supplied list values
syn = sim.StaticSynapse(weight=1.5, delay=5)
proj = sim.Projection(input, receiver, conn, syn, receptor_type="excitatory")

input.record(["spikes"])
receiver.record(["v", "spikes"])

pre_weights_delays = proj.get(["weight", "delay"], format="list")

sim.run(200.0)

voltages = receiver.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

post_weights_delays = proj.get(["weight", "delay"], format="list")

print(voltages)
print(spikes)
print(spikes_rec)
print(pre_weights_delays)
print(post_weights_delays)

sim.end()

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spike source array')

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes_rec], [i[0] for i in spikes_rec], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spikes on receiver')

pylab.figure()
pylab.xlabel('Time/ms')
pylab.ylabel('v')
pylab.title('v')
pylab.plot([v[1] for v in voltages], [v[2] for v in voltages])
pylab.show()
