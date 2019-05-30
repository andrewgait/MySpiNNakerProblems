import pylab
import spynnaker8 as sim

sim.setup(timestep=1.0)

n_neurons = 2

spike_times = [[i+1] for i in range(n_neurons)]
print('spike_times', spike_times)
input = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times), label='input')
receiver = sim.Population(n_neurons, sim.IF_curr_exp(), label='receiver')

# conn = sim.FixedProbabilityConnector(0.5)
alltoall = sim.AllToAllConnector()
onetoone = sim.OneToOneConnector()

# Two projections between the same populations
syn = sim.StaticSynapse(weight=2.5, delay=3)
syn2 = sim.StaticSynapse(weight=2.0, delay=5)
alltoall_proj = sim.Projection(input, receiver, alltoall, syn,
                      receptor_type="excitatory", label="alltoall")
onetoone_proj = sim.Projection(input, receiver, onetoone, syn2,
                       receptor_type="inhibitory", label="onetoone")

input.record(["spikes"])
receiver.record(["v", "spikes"])

sim.run(200.0)

alltoall_weights_delays = alltoall_proj.get(["weight", "delay"], format="list")
onetoone_weights_delays = onetoone_proj.get(["weight", "delay"], format="list")

voltages = receiver.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

sim.end()

print('alltoall', alltoall)
print('onetoone', onetoone)
print('alltoall_weights_delays:', alltoall_weights_delays)
print('onetoone_weights_delays:', onetoone_weights_delays)

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