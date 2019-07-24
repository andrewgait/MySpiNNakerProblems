from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

import pickle

data = pickle.load(open('test_data.pk', 'rb'))
runtime = 2500

# entry = data[(0, 0)]

panels = []

for (i, j) in data:
    panels.append(Panel(data[(i, j)].segments[0].spiketrains,
                        xlabel="Time/ms {}-{}".format(i, j), xticks=True,
                        yticks=True, markersize=0.5, xlim=(0, runtime))),

Figure(*panels,
       title="CLester run: spikes",
       annotations="Simulated with SpiNNaker"
)

plt.show()
