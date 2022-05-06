import pylab
import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)

n_neurons = 2

spike_times = [[i+1] for i in range(n_neurons)]
print('spike_times', spike_times)
input = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times), label='input')
receiver = sim.Population(n_neurons, sim.IF_curr_exp(), label='receiver')

onetoone = sim.OneToOneConnector()
alltoall = sim.AllToAllConnector()
fixedprob = sim.FixedProbabilityConnector(0.25)
fixedtotal = sim.FixedTotalNumberConnector(3, with_replacement=False)
fromlist = sim.FromListConnector(([0, 0, 1.2, 2],[1, 0, 1.1, 1]))

# different StaticSynapses for testing
syn = sim.StaticSynapse(weight=2.5, delay=3)
syn2 = sim.StaticSynapse(weight=1.5, delay=4)
syn3 = sim.StaticSynapse(weight=2.0, delay=5)
syn4 = sim.StaticSynapse(weight=3.0, delay=6)
syn5 = sim.StaticSynapse(weight=3.5, delay=7)

# Two projections between the same populations
alltoall_proj = sim.Projection(input, receiver, alltoall, syn,
                               receptor_type="excitatory", label="alltoall")
fromlist_proj = sim.Projection(input, receiver, fromlist, syn5,
                               receptor_type="excitatory", label="fromlist")
onetoone_proj = sim.Projection(input, receiver, onetoone, syn3,
                               receptor_type="inhibitory")  #, label="onetoone")
fixedprob_proj = sim.Projection(input, receiver, fixedprob, syn2,
                                receptor_type="excitatory", label="fixedprob")
fixedtotal_proj = sim.Projection(input, receiver, fixedtotal, syn4,
                                 receptor_type="excitatory", label="fixedtotal")

input.record(["spikes"])
receiver.record(["v", "spikes"])

sim.run(200.0)

alltoall_weights_delays = alltoall_proj.get(["weight", "delay"], format="list")
onetoone_weights_delays = onetoone_proj.get(["weight", "delay"], format="list")
fixedtotal_weights_delays = fixedtotal_proj.get(["weight", "delay"], format="list")
fromlist_weights_delays = fromlist_proj.get(["weight", "delay"], format="list")
fixedprob_weights_delays = fixedprob_proj.get(["weight", "delay"], format="list")

voltages = receiver.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

sim.end()

print('alltoall', alltoall)
print('alltoall_proj', alltoall_proj)
print('alltoall_weights_delays:', alltoall_weights_delays)
print('fixedprob', fixedprob)
print('fixedprob_proj', fixedprob_proj)
print('fixedprob_weights_delays:', fixedprob_weights_delays)
print('fixedtotal', fixedtotal)
print('fixedtotal_proj', fixedtotal_proj)
print('fixedtotal_weights_delays:', fixedtotal_weights_delays)
print('onetoone', onetoone)
print('onetoone_proj', onetoone_proj)
print('onetoone_weights_delays:', onetoone_weights_delays)
print('fromlist', fromlist)
print('fromlist_proj', fromlist_proj)
print('fromlist_weights_delays:', fromlist_weights_delays)

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