import pylab
import spynnaker8 as sim

sim.setup(timestep=1.0)

n_neurons = 2

spike_times = [[i+1] for i in range(n_neurons)]
print('spike_times', spike_times)
input = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times), label='input')
receiver = sim.Population(n_neurons, sim.IF_curr_exp(), label='receiver')

# conn = sim.FixedProbabilityConnector(0.5)
conn = sim.AllToAllConnector()
conn2 = sim.OneToOneConnector()

# Two projections between the same populations
syn = sim.StaticSynapse(weight=2.5, delay=3)
syn2 = sim.StaticSynapse(weight=2.0, delay=5)
proj = sim.Projection(input, receiver, conn, syn,
                      receptor_type="excitatory", label="proj1")
proj2 = sim.Projection(input, receiver, conn2, syn2,
                       receptor_type="inhibitory", label="proj2")

input.record(["spikes"])
receiver.record(["v", "spikes"])

sim.run(200.0)

post_weights_delays = proj.get(["weight", "delay"], format="list")
post_weights_delays2 = proj2.get(["weight", "delay"], format="list")

voltages = receiver.spinnaker_get_data("v")
spikes = input.spinnaker_get_data("spikes")
spikes_rec = receiver.spinnaker_get_data("spikes")

sim.end()

print('proj', proj)
print('proj2', proj2)
print('post_weights_delays:', post_weights_delays)
print('post_weights_delays2:', post_weights_delays2)

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