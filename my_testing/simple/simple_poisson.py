import pylab
import pyNN.spiNNaker as sim
sim.setup(timestep=1.0)
poisson = sim.Population(2, sim.SpikeSourcePoisson(
    duration=1.0e10, rate=100.0, start=0.0))
receiver = sim.Population(2, sim.IF_curr_exp())

#conn = sim.AllToAllConnector()
connections = [
(0, 0, 1.0, 7.0),
(1, 0, 2.0, 7.0),
(0, 1, 3.0, 7.0),
(1, 1, 4.0, 8.0)
]

conn = sim.FromListConnector(connections)
syn = sim.StaticSynapse(weight=0.5, delay=1)
sim.Projection(presynaptic_population=poisson,
               postsynaptic_population=receiver,
               connector=conn, synapse_type=syn, receptor_type="excitatory")
#sim.Projection(poisson, receiver, conn,
#               synapse_type=syn, receptor_type="excitatory")
receiver.record(["v", "spikes"])
poisson.record("spikes")

# poisson.set(rate=1000.0)

sim.run(2000.0)

# poisson.set(rate=[100.0,100.0])
#
# sim.run(200.0)

voltages = receiver.spinnaker_get_data("v")
spikes = poisson.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

sim.end()
print(voltages)
print(spikes)
print(spikes_rec)

pylab.figure()
pylab.xlim((0, 400.0))
pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('Spike source poisson')

pylab.figure()
pylab.xlim((0, 400.0))
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
