import math
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyNN.spiNNaker as sim
import numpy as np

plt.rc('animation', ffmpeg_path='/opt/local/bin/ffmpeg')

sim.setup(1.0)

n_neurons = 4
# run long enough to form all connections
sim_time = 400

gd = int(math.sqrt(n_neurons))
print('Structural plasticity formation, ', n_neurons, ' neurons, grid, ', gd)

# stimulus population
stim = sim.Population(n_neurons,
                      sim.SpikeSourceArray(range(0,sim_time,sim_time//60)),
                      label="stim")

# These populations should experience formation
pop = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop")

# Formation with random selection (0 probability elimination)
# proj = sim.Projection(
#     stim, pop, sim.FromListConnector([]), sim.StructuralMechanismStatic(
#         partner_selection=sim.LastNeuronSelection(),
#         formation=sim.DistanceDependentFormation(
#             [gd, gd], p_form_forward=1.0, sigma_form_forward=10.5),
#         elimination=sim.RandomByWeightElimination(4.0, 0, 0),
#         f_rew=1000, initial_weight=2.0, initial_delay=3.0,
#         s_max=n_neurons, seed=0, weight=0.0, delay=1.0,
#         with_replacement=False))
proj = sim.Projection(
    stim, pop, sim.FromListConnector([]), sim.StructuralMechanismSTDP(
        partner_selection=sim.LastNeuronSelection(),
        formation=sim.DistanceDependentFormation(
            [gd, gd], p_form_forward=1.0, sigma_form_forward=10.5),
        elimination=sim.RandomByWeightElimination(4.0, 0, 0),
        f_rew=1000, initial_weight=2.0, initial_delay=3.0,
        s_max=n_neurons, seed=0, weight=0.0, delay=1.0,
        with_replacement=False,
        timing_dependence=sim.SpikePairRule(
            tau_plus=20., tau_minus=20.0, A_plus=0.1, A_minus=0.02),
        weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=1.)))


# set stuff to record
pop.record("spikes")
pop.record("v")
pop.record("rewiring")
pop.record("packets-per-timestep")

# Get the initial connections
initial_conns = proj.get(["weight", "delay"], "list")
initial_conns_array = proj.get(["weight"], "array")

# run for enough time that every connection forms
# sim.run(sim_time)
sim.run(sim_time//2)

# Add another population
pop2 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop2")

# Add another projection: Formation with random selection (0 probability elimination)
# proj2 = sim.Projection(
#     stim, pop2, sim.FromListConnector([]), sim.StructuralMechanismStatic(
#         partner_selection=sim.LastNeuronSelection(),
#         formation=sim.DistanceDependentFormation(
#             [gd, gd], p_form_forward=1.0, sigma_form_forward=10.5),
#         elimination=sim.RandomByWeightElimination(4.0, 0, 0),
#         f_rew=1000, initial_weight=2.0, initial_delay=3.0,
#         s_max=n_neurons, seed=0, weight=0.0, delay=1.0,
#         with_replacement=False))

sim.reset()

sim.run(sim_time//2)

# get data back
spikes = pop.get_data("spikes")
post_v = pop.get_data("v")
print("post v: ", post_v.segments[0].filter(name='v')[0])

Figure(
    # raster plot of the post neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.5, xlim=(0, sim_time)),
    # plot v for post neuron
    Panel(post_v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, sim_time)),
    Panel(spikes.segments[1].spiketrains,
          yticks=True, markersize=0.5, xlim=(0, sim_time)),
    # plot v for post neuron
    Panel(post_v.segments[1].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, sim_time)),
    title="Structural plasticity formation to full",
)
plt.show()

pps = pop.get_data("packets-per-timestep")

rewiring = pop.get_data("rewiring")
# rewiring_array = rewiring.segments[0].filter(name='rewiring')[0]
rewiring_events_form = rewiring.segments[0].events[0]
rewiring_events_elim = rewiring.segments[0].events[1]
rewiring_events_form2 = rewiring.segments[1].events[0]
rewiring_events_elim2 = rewiring.segments[1].events[1]

# print("spikes: ", spikes.segments[0].spiketrains)
print("rewiring: ", rewiring, rewiring_events_form, rewiring_events_elim)
print("rewiring labels: ", rewiring_events_form.labels)
print("rewiring 2: ", rewiring, rewiring_events_form2, rewiring_events_elim2)
print("rewiring labels 2: ", rewiring_events_form2.labels)
# print("post v: ", post_v.segments[0].filter(name='v')[0])

# Get the final connections
conns = list(proj.get(["weight", "delay"], "list"))

print("Initial connections")
print(len(list(initial_conns)), list(initial_conns))
print("Final connections")
print(len(conns), conns)

# end sim
sim.end()

# rewiring_decoded = []
rewiring_adds = []
rewiring_removals = []

for form_label, form_time in zip(rewiring_events_form.labels,
                                 rewiring_events_form.times):
    neuron_IDs = form_label.split("_")
    rewiring_adds.append(
        [form_time.item(), int(neuron_IDs[0]), int(neuron_IDs[1]), 1])

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

# probably possible to create an animation of "forming" connections
print(initial_conns_array)
print(rewiring_adds[-1])

anim_length = int(rewiring_adds[-1][0]) + 20

conns_arrays = []
conns_arrays.append(initial_conns_array)

for i in range(anim_length):
    initial_conns_array = initial_conns_array.copy()

    for n in range(len(rewiring_adds)):
        add = rewiring_adds[n]
        if (int(add[0]) == i):
            initial_conns_array[add[1]][add[2]] = 1

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
im_ani.save('connections_forming.mp4', writer=my_writer)

plt.show()
