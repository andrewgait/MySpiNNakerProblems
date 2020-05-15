from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import spynnaker8 as sim

sim.setup(1.0)

n_neurons = 4

# stimulus population
stim = sim.Population(n_neurons, sim.SpikeSourceArray(range(10)), label="stim")

# These populations should experience formation
pop = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop")

# Formation with random selection (0 probability elimination)
proj = sim.Projection(
    stim, pop, sim.FromListConnector([]), sim.StructuralMechanismStatic(
        partner_selection=sim.LastNeuronSelection(),
        formation=sim.DistanceDependentFormation([2, 2], 1.0),
        elimination=sim.RandomByWeightElimination(4.0, 0, 0),
        f_rew=1000, initial_weight=4.0, initial_delay=3.0,
        s_max=4, seed=0, weight=0.0, delay=1.0))

# set stuff to record
pop.record("spikes")
pop.record("struct_pl")

# Get the initial connections
initial_conns = proj.get(["weight", "delay"], "list")

# run for enough time that every connection forms
sim_time = 1000
sim.run(sim_time)

# get data back
spikes = pop.get_data("spikes")
struct_pl = pop.get_data("struct_pl")
struct_pl_array = struct_pl.segments[0].filter(name='struct_pl')[0]

print("spikes: ", spikes.segments[0].spiketrains)
print("struct_pl: ", struct_pl, struct_pl_array)

struct_pl_decoded = []

struct_pl_adds = []

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
            struct_pl_adds.append([i, preidval, postidval, addedremovedval])

    struct_pl_decoded.append(preid)
    struct_pl_decoded.append(postid)
    struct_pl_decoded.append(addedremoved)

print("struct_pl_decoded: ", struct_pl_decoded)
print("struct_pl_adds: ", struct_pl_adds, len(struct_pl_adds))

# Get the final connections
conns = list(proj.get(["weight", "delay"], "list"))

print("Initial connections")
print(list(initial_conns))
print("Final connections")
print(conns)

Figure(
    # raster plot of the neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, sim_time)),
    title="Structural plasticity formation to full",
)
plt.show()

sim.end()

