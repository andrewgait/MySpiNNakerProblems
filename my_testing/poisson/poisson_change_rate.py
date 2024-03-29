import pyNN.spiNNaker as p
import numpy

def print_spikes(trains):
    nseg = len(trains.segments)
    for i in range(nseg):
        trains1 = trains.segments[i].spiketrains
        print("segment ", i, " ", trains1[0])


to_plot_wgts = False

p.setup(1)

simtime = 1000

pop_src2 = p.Population(1, p.SpikeSourcePoisson(rate=0), label="drive",
                        additional_parameters={"seed": 1000})
pop_ex = p.Population(1, p.IF_curr_exp(), label="test")

conn = p.OneToOneConnector()
proj2 = p.Projection(pop_src2,  pop_ex,  conn,
                     synapse_type=p.StaticSynapse(weight=2.0),
                     receptor_type='excitatory')

print("connector space: ", conn.space.AXES)

pop_src2.record(['spikes'])
pop_ex.record('spikes')
nseg = 0

pop_src2.set(rate=100)
p.run(simtime)
print_spikes(pop_ex.get_data('spikes'))
p.reset()
pop_src2.set(rate=50)
p.run(simtime)
print_spikes(pop_ex.get_data('spikes'))
p.reset()
pop_src2.set(rate=20)
p.run(simtime)
print_spikes(pop_ex.get_data('spikes'))
p.reset()

p.end()
print("\n job done")