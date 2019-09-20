import pylab
import os
import numpy
import spynnaker8 as sim

sim.setup(timestep=1.0)

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 200)

# cell_params_lif = {'cm': 0.25,
#                    'i_offset': 0.0,
#                    'tau_m': 20.0,
#                    'tau_refrac': 2.0,
#                    'tau_syn_E': 0.1,
#                    'tau_syn_I': 0.1,
#                    'v_reset': -70.0,
#                    'v_rest': -65.0,
#                    'v_thresh': -50.0
#                    }

popAsize = 3000
popBsize = 3000

input = sim.Population(popAsize, sim.SpikeSourceArray([[1] for i in range(popAsize)]), label='input')
receiverA = sim.Population(popAsize, sim.IF_curr_exp(), label='receiverA')
receiverB = sim.Population(popBsize, sim.IF_curr_exp(), label='receiverB')

ExcConnector = []
wt = 5.0
for i in range(popAsize):
    for j in range(popBsize):
        p = 1.0/(j+1)
        wtB = wt*p  # wt weight required
        ExcConnector += [(i,j,wtB,1.0)]

# path1 = "test_larger.connections"
# if os.path.exists(path1):
#     os.remove(path1)
#
# current_file_path = os.path.dirname(os.path.abspath(__file__))
# file1 = os.path.join(current_file_path, path1)
# numpy.savetxt(file1, ExcConnector) #,
              #header='columns = ["i", "j", "weight", "delay"]')
# print(ExcConnector)

#conn = sim.AllToAllConnector()
conn = sim.FromListConnector(ExcConnector)
#conn = sim.FromFileConnector(file1)

# conn = sim.FromListConnector(connection_list)
# conn = sim.FromListConnector(connections_test)

# Here I am testing that these don't overwrite the supplied list values
syn = sim.StaticSynapse(weight=5.0, delay=1)
proj1 = sim.Projection(input, receiverA, sim.OneToOneConnector(), syn, receptor_type="excitatory")
proj2 = sim.Projection(receiverA, receiverB, conn, syn, receptor_type="excitatory")

input.record(["spikes"])
receiverA.record(["v", "spikes"])
receiverB.record(["v", "spikes"])

# pre_weights_delays = proj.get(["weight", "delay"], format="list")

sim.run(20.0)

voltages = receiverA.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_recA = receiverA.spinnaker_get_data("spikes")
spikes_recB = receiverB.spinnaker_get_data("spikes")

post_weights_delays = proj1.get(["weight", "delay"], format="list")
post_weights_delays2 = proj2.get(["weight", "delay"], format="list")

sim.end()

print(voltages)
print(spikes)
print(spikes_recA)
print(spikes_recB)
# print(pre_weights_delays)
print(post_weights_delays)
print(post_weights_delays2)

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spike source poisson')
pylab.show()

pylab.figure()
pylab.xlabel('Time/ms')
pylab.ylabel('v')
pylab.title('v')
pylab.plot([v[1] for v in voltages], [v[2] for v in voltages])
pylab.show()

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes_recA], [i[0] for i in spikes_recA], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spikes on receiverA')
pylab.show()

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes_recB], [i[0] for i in spikes_recB], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spikes on receiverB')
pylab.show()

