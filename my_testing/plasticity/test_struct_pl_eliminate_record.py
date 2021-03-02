from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import spynnaker8 as sim

sim.setup(1.0)

n_neurons = 9

# run for long enough that all connections are eliminated
sim_time = 2000

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
        formation=sim.DistanceDependentFormation([3, 3], 0.0),
        elimination=sim.RandomByWeightElimination(4.0, 1.0, 1.0),
        f_rew=1000, initial_weight=4.0, initial_delay=3.0,
        s_max=9, seed=0, weight=3.0, delay=1.0))

# record stuff
stim.record("spikes")
pop.record("spikes")
pop.record("v")
pop.record("struct_pl")
# pop.record(["v", "gsyn_exc", "gsyn_inh"])

# Get the initial connections
initial_conns = proj.get(["weight", "delay"], "list")

sim.run(sim_time)

# get data
pre_spikes = stim.get_data("spikes")
spikes = pop.get_data("spikes")
post_v = pop.get_data("v")
struct_pl = pop.get_data("struct_pl")
struct_pl_array = struct_pl.segments[0].filter(name='struct_pl')[0]

print("pre_spikes: ", pre_spikes.segments[0].spiketrains)
print("spikes: ", spikes.segments[0].spiketrains)
print("post v: ", post_v.segments[0].filter(name='v')[0])
print("struct_pl: ", struct_pl, struct_pl_array)

# Get the final connections
conns = list(proj.get(["weight", "delay"], "list"))

print("Initial connections")
print(list(initial_conns))
print("Final connections")
print(conns)

# end simulation
sim.end()

# code to decode the numbers in struct_pl
struct_pl_decoded = []
struct_pl_removals = []

for i in range(sim_time):
    preid = []
    postid = []
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
            postidval = int(bin_postid, 2)
            addedremovedval = int(bin_addedremoved, 2)
            preid.append(preidval)
            postid.append(postidval)
            addedremoved.append(addedremovedval)
            struct_pl_removals.append([i, preidval, postidval, addedremovedval])

    struct_pl_decoded.append(preid)
    struct_pl_decoded.append(postid)
    struct_pl_decoded.append(addedremoved)

# print("struct_pl_decoded: ", struct_pl_decoded)
# print("struct_pl_removals: ", len(struct_pl_removals), struct_pl_removals)

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


