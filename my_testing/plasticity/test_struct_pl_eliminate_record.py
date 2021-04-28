from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import spynnaker8 as sim
import numpy as np
import math

plt.rc('animation', ffmpeg_path='/opt/local/bin/ffmpeg')

sim.setup(1.0)

n_neurons = 25

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 10)
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 10)

# run for long enough that all connections are eliminated
sim_time = 10000

gd = int(math.sqrt(n_neurons))
print('Structural plasticity elimination, ', n_neurons, ' neurons, grid, ', gd)

# stimulation population
stim = sim.Population(n_neurons, sim.SpikeSourceArray(
    range(0,sim_time,sim_time//40)), label="stim")

# These populations should experience elimination
pop = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop")

# Elimination with random selection (0 probability formation)
proj = sim.Projection(
    stim, pop, sim.AllToAllConnector(),
    sim.StructuralMechanismStatic(
        partner_selection=sim.RandomSelection(),
        formation=sim.DistanceDependentFormation([gd, gd], 0.0),
        elimination=sim.RandomByWeightElimination(4.0, 1.0, 1.0),
        f_rew=5000, initial_weight=1.0, initial_delay=3.0,
        s_max=n_neurons, seed=0, weight=1.0, delay=1.0))

# record stuff
stim.record("spikes")
pop.record("spikes")
pop.record("v")
pop.record("rewiring")
# pop.record(["v", "gsyn_exc", "gsyn_inh"])

# Get the initial connections
initial_conns = proj.get(["weight", "delay"], "list")
initial_conns_array = proj.get(["weight"], "array")

sim.run(sim_time)

# get data
pre_spikes = stim.get_data("spikes")
spikes = pop.get_data("spikes")
post_v = pop.get_data("v")
rewiring = pop.get_data("rewiring")
# rewiring_array = rewiring.segments[0].filter(name='rewiring')[0]
rewiring_events_form = rewiring.segments[0].events[0]
rewiring_events_elim = rewiring.segments[0].events[1]

# print("pre_spikes: ", pre_spikes.segments[0].spiketrains)
# print("spikes: ", spikes.segments[0].spiketrains)
print("rewiring: ", rewiring, rewiring_events_form, rewiring_events_elim)
print("rewiring labels: ", rewiring_events_elim.labels)
# print("post v: ", post_v.segments[0].filter(name='v')[0])

# Get the final connections
conns = list(proj.get(["weight", "delay"], "list"))

print("Initial connections")
print(list(initial_conns))
print("Final connections")
print(conns)

# end simulation
sim.end()

# rewiring_decoded = []
rewiring_adds = []
rewiring_removals = []

for form_label, form_time in zip(rewiring_events_elim.labels,
                                 rewiring_events_elim.times):
    neuron_IDs = form_label.split("_")
    rewiring_removals.append(
        [form_time.item(), int(neuron_IDs[0]), int(neuron_IDs[1]), 0])

# for i in range(sim_time):
#     preid = []
#     postid = []
#     addedremoved = []
#     for j in range(n_neurons):
#         if (int(rewiring_array[i][j]) == -1):
#             preid.append(-1)
#             postid.append(-1)
#             addedremoved.append(-1)
#         else:
#             bin_val = bin(int(rewiring_array[i][j]))[2:]  # take the "0b" off
#             # front-pad with zeros to size 32
#             len_bin = len(bin_val)
#             for n in range(32-len_bin):
#                 bin_val = "0"+bin_val
#
#             bin_addedremoved = bin_val[-1]
#             bin_preid = "0b"+(bin_val[:31])
#             preidval = int(bin_preid, 2)
#             postidval = j
#             addedremovedval = int(bin_addedremoved, 2)
#             preid.append(preidval)
#             postid.append(postidval)
#             addedremoved.append(addedremovedval)
#             rewiring_adds.append([i, preidval, postidval, addedremovedval])
#
#     rewiring_decoded.append([i, preid, postid, addedremoved])

# print("rewiring_decoded: ", len(rewiring_decoded), rewiring_decoded)
print("rewiring_adds: ", len(rewiring_adds), rewiring_adds)
print("rewiring_removals: ", len(rewiring_removals), rewiring_removals)

Figure(
    # raster plot of the pre-neuron spike times
    Panel(pre_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.5, xlim=(0, sim_time)),
    # raster plot of the post-neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.5, xlim=(0, sim_time)),
    # plot v for post neuron
    Panel(post_v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, sim_time)),
    title="Structural plasticity elimination to empty",
)
plt.show()

# probably possible to create an animation of "removing" connections
print(initial_conns_array)
print(rewiring_removals[-1])

anim_length = int(rewiring_removals[-1][0]) + 20

conns_arrays = []
conns_arrays.append(initial_conns_array)

for i in range(anim_length):
    initial_conns_array = initial_conns_array.copy()

    for n in range(len(rewiring_removals)):
        remove = rewiring_removals[n]
        if (int(remove[0]) == i):
            initial_conns_array[remove[1]][remove[2]] = 0

    conns_arrays.append(initial_conns_array)

print(conns_arrays[0])
print(conns_arrays[10])
print(conns_arrays[-1])

x = np.linspace(0, n_neurons, len(conns_arrays[0][0])+1)
y = np.linspace(0, n_neurons, len(conns_arrays[0])+1)
xmesh, ymesh = np.meshgrid(x,y)

fig = plt.figure()
ax = fig.add_subplot(111)

ims = []
print("Animating ", len(conns_arrays), " connection arrays")
conn_range = range(len(conns_arrays))
for n in conn_range:
    mess = "Time "+str(n)+" of "+str(anim_length)
    ttl = plt.text(
        0.5, 1.01, mess, ha="center", va="bottom", transform=ax.transAxes)
# for n in range(100):
    if n % 200 == 0:
        print(n)
#     array = np.flipud(np.array(conns_arrays[n]))
# print(array)
    plotcolor = ax.pcolor(xmesh, ymesh, conns_arrays[n])
    ims.append([plotcolor, ttl,])

im_ani = animation.ArtistAnimation(
    fig, ims, interval=10, repeat_delay=10000, blit=False)
my_writer = animation.FFMpegWriter(metadata={'code':'andrewgait'})
im_ani.save('connections_eliminating.mp4', writer=my_writer)

plt.show()
