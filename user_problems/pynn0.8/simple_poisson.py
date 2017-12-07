import pylab
import spynnaker8 as sim
sim.setup()
poisson = sim.Population(1, sim.SpikeSourcePoisson(duration=1.0e10,
                                                   rate=0.0, start=0.0))
receiver = sim.Population(1, sim.IF_curr_exp())

conn = sim.AllToAllConnector()
syn = sim.StaticSynapse(weight=0.15, delay=1.0)
sim.Projection(presynaptic_population=poisson,
               postsynaptic_population=receiver,
               connector=conn, synapse_type=syn, receptor_type="excitatory")
#sim.Projection(poisson, receiver, conn,
#               synapse_type=syn, receptor_type="excitatory")
receiver.record(["v", "spikes"])
poisson.record("spikes")

# poisson.set(rate=1000.0)

sim.run(20.0)

poisson.set(rate=1000.0)

sim.run(20.0)

voltages = receiver.spinnaker_get_data("v")
spikes = poisson.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

sim.end()
print voltages
print spikes
print spikes_rec

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
