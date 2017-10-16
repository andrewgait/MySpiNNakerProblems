import spynnaker7.pyNN as pyNN

from spynnaker7.pyNN.external_devices import SpynnakerLiveSpikesConnection, SpynnakerExternalDevicePluginManager


def create_targets(size=40, height=20):
    targets = []
    for i in range(size):
        target_pop = pyNN.Population(height, pyNN.IF_curr_exp, {'v_reset': -70.0},
                                     label="target_{0}".format(i))
        SpynnakerExternalDevicePluginManager.activate_live_output_for(target_pop,
                                                                      database_notify_host="localhost",
                                                                      database_notify_port_num=19996)
        targets.append(target_pop)
    return targets


def create_sources(size=40, height=20):
    sources = []
    for i in range(size):
        source = pyNN.Population(height, pyNN.SpikeSourceArray,
                                 {'spike_times': [[10]]}, label="source_{}".format(i))
        sources.append(source)
    return sources


pyNN.setup(timestep=0.2, min_delay=0.2, max_delay=2.0, threads=4)

sources = create_sources(size=20)
targets = create_targets(size=20)

for s, t in zip(sources, targets):
    pyNN.Projection(s, t, pyNN.OneToOneConnector(weights=10, delays=0.2))

labels = [t.label for t in targets]
live_connection = SpynnakerLiveSpikesConnection(receive_labels=labels, local_port=19996, send_labels=None)


def print_spikes(label, timestamp, neuron_ids):
    print(label, timestamp, neuron_ids)

for t in targets:
    live_connection.add_receive_callback(t.label, print_spikes)

pyNN.run(100)
pyNN.end()