import math
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import spynnaker8 as sim
import numpy as np

plt.rc('animation', ffmpeg_path='/opt/local/bin/ffmpeg')

sim.setup(1.0)

n_neurons = 9
# run long enough to form all connections
sim_time = 3000

gd = int(math.sqrt(n_neurons))
print('Structural plasticity formation, ', n_neurons, ' neurons, grid, ', gd)

# stimulus population
stim = sim.Population(n_neurons,
                      sim.SpikeSourceArray(range(0,sim_time,sim_time//60)),
                      label="stim")

# These populations should experience formation
pop = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop")

# Formation with random selection (0 probability elimination)
proj = sim.Projection(
    stim, pop, sim.FromListConnector([]), sim.StructuralMechanismStatic(
        partner_selection=sim.LastNeuronSelection(),
        formation=sim.DistanceDependentFormation(
            [gd, gd], p_form_forward=1.0, sigma_form_forward=5.5),
        elimination=sim.RandomByWeightElimination(4.0, 0, 0),
        f_rew=1000, initial_weight=2.0, initial_delay=3.0,
        s_max=n_neurons, seed=0, weight=0.0, delay=1.0,
        with_replacement=False))

# set stuff to record
pop.record("spikes")
pop.record("struct_pl")
pop.record("v")

# Get the initial connections
initial_conns = proj.get(["weight", "delay"], "list")
initial_conns_array = proj.get(["weight"], "array")

# run for enough time that every connection forms
sim.run(sim_time)

# get data back
spikes = pop.get_data("spikes")
struct_pl = pop.get_data("struct_pl")
struct_pl_array = struct_pl.segments[0].filter(name='struct_pl')[0]
post_v = pop.get_data("v")

print("spikes: ", spikes.segments[0].spiketrains)
print("struct_pl: ", struct_pl, struct_pl_array)
print("post v: ", post_v.segments[0].filter(name='v')[0])

# Get the final connections
conns = list(proj.get(["weight", "delay"], "list"))

print("Initial connections")
print(list(initial_conns))
print("Final connections")
print(conns)

# end sim
sim.end()

struct_pl_decoded = []
struct_pl_adds = []

for i in range(sim_time):
    preid = []
    postid = []
    postlocalid = []
    addedremoved = []
    for j in range(n_neurons):
        if (int(struct_pl_array[i][j]) == -1):
            preid.append(-1)
            postid.append(-1)
            addedremoved.append(-1)
        else:
            bin_val = bin(int(struct_pl_array[i][j]))[2:]  # take the "0b" off
            # front-pad with zeros to size 32
            len_bin = len(bin_val)
            for n in range(32-len_bin):
                bin_val = "0"+bin_val

            bin_addedremoved = bin_val[-1]
            bin_preid = "0b"+(bin_val[:23])
            bin_postid = "0b"+(bin_val[23:31])
            preidval = int(bin_preid, 2)
            postlocalidval = int(bin_postid, 2)
            postidval = j
            addedremovedval = int(bin_addedremoved, 2)
            preid.append(preidval)
            postlocalid.append(postlocalidval)
            postid.append(postidval)
            addedremoved.append(addedremovedval)
            struct_pl_adds.append([i, preidval, postidval, addedremovedval])

    struct_pl_decoded.append([i, preid, postid, addedremoved])

# print("struct_pl_decoded: ", len(struct_pl_decoded), struct_pl_decoded)
print("struct_pl_adds: ", len(struct_pl_adds), struct_pl_adds)

Figure(
    # raster plot of the post neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.5, xlim=(0, sim_time)),
    # plot v for post neuron
    Panel(post_v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, sim_time)),
    title="Structural plasticity formation to full",
)
plt.show()

# probably possible to create an animation of "forming" connections
print(initial_conns_array)
print(struct_pl_adds[-1])

anim_length = struct_pl_adds[-1][0] + 10

conns_arrays = []
conns_arrays.append(initial_conns_array)

add = struct_pl_adds.pop(0)
print(add)

for i in range(anim_length):
    initial_conns_array = initial_conns_array.copy()
    if (add[0] == i):
        initial_conns_array[add[1]][add[2]] = 1
        if (len(struct_pl_adds)):
            add = struct_pl_adds.pop(0)

    conns_arrays.append(initial_conns_array)

print(conns_arrays[0])
print(conns_arrays[10])

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
    ttl = plt.text(0.5, 1.01, mess, ha="center", va="bottom",
                   transform=ax.transAxes)
# for n in range(100):
    if n % 20 == 0:
        print(n)
    array = np.flipud(np.array(conns_arrays[n]))
# print(array)
    plotcolor = ax.pcolor(xmesh, ymesh, array)
    ims.append([plotcolor, ttl,])


im_ani = animation.ArtistAnimation(fig, ims, interval=10, repeat_delay=10000,
                                   blit=False)
my_writer = animation.FFMpegWriter(metadata={'code':'andrewgait'})
im_ani.save('connections_forming.mp4', writer=my_writer)

plt.show()
