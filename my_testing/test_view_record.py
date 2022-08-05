import pyNN.spiNNaker as sim
import math

V_PATTERN = [-65.0, -64.024658203125, -63.09686279296875,
             -62.214324951171875,
             -61.37481689453125, -60.576263427734375, -59.816650390625,
             -59.09405517578125, -58.406707763671875, -57.752899169921875,
             -57.130950927734375, -56.539337158203125, -55.976593017578125,
             -55.4412841796875, -54.93206787109375, -54.44769287109375,
             -53.9869384765625, -53.54864501953125, -53.131744384765625,
             -52.73516845703125, -52.357940673828125, -51.999114990234375,
             -51.65777587890625, -51.33306884765625, -51.024200439453125,
             -50.73040771484375, -50.450927734375, -50.185089111328125]
V_COUNT = len(V_PATTERN)

sim.setup(timestep=1)
simtime = 100
n_neurons = 10
label = "test"
v_start = V_PATTERN * int(math.ceil(n_neurons/V_COUNT))
v_start = v_start[:n_neurons]
pop = sim.Population(n_neurons,
                     sim.IF_curr_exp(i_offset=1, tau_refrac=0),
                     label=label)
pop.initialize(v=v_start)

# v_rec_indexes = [2, 4, 6, 8]
view = pop[2, 4, 6, 8]
view2 = pop[2, 3, 4]

view.record(['v'])
# pop.record(['v'])
pop.record(["spikes"])

sim.run(simtime)

neo_spikes = pop.get_data("spikes")
spikes = neo_spikes.segments[0].spiketrains
neo_v = view2.get_data("v")
v = neo_v.segments[0].filter(name="v")[0]

print(v)
print(spikes)

sim.end()
