import pylab
import os
import numpy
import spynnaker8 as sim

sim.setup(timestep=1.0)
input = sim.Population(1, sim.SpikeSourceArray([[1]]), label='input')
receiver = sim.Population(2, sim.IF_curr_exp(), label='receiver')

columns = ["i", "j", "delay", "weight"]
connection_list = [
    (0, 0, 1.0, 10.0),
    (0, 1, 1.0, -1.0)
    ]

path1 = "test.connections"
if os.path.exists(path1):
    os.remove(path1)

current_file_path = os.path.dirname(os.path.abspath(__file__))
file1 = os.path.join(current_file_path, path1)
numpy.savetxt(file1, connection_list,
              header='columns = ["i", "j", "delay", "weight"]')

conn = sim.FromFileConnector(file1)
# conn = sim.FromListConnector(connection_list)  # , column_names=columns)

# Here I am testing that these don't overwrite the supplied list values
syn = sim.StaticSynapse(weight=1.5, delay=5)
proj = sim.Projection(input, receiver, conn, syn, receptor_type="excitatory")

input.record(["spikes"])
receiver.record(["v", "spikes"])

pre_weights_delays = proj.get(["weight", "delay"], format="list")

sim.run(20.0)

voltages = receiver.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

post_weights_delays = proj.get(["weight", "delay"], format="list")

sim.end()

print(voltages)
print(spikes)
print(spikes_rec)
print(pre_weights_delays)
print(post_weights_delays)

pylab.figure()
pylab.xlim((0, 40.0))
pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spike source poisson')

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
