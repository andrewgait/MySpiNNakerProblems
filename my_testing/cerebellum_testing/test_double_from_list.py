import pyNN.spiNNaker as sim
import numpy as np
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

# sim.set_number_of_neurons_per_core(sim.IF_cond_exp, 64)
size1 = 1600
size2 = 10
pop1 = sim.Population(size1, sim.IF_cond_exp, label='pop1')
pop2 = sim.Population(size2, sim.IF_cond_exp, label='pop2')

pop1.set_max_atoms_per_core(32)
pop2.set_max_atoms_per_core(1)

aa_pc = np.loadtxt("conn_aa_pc.txt")
print("check: aa_pc ", len(aa_pc), aa_pc[0])

pf_pc = np.loadtxt("conn_pf_pc.txt")
print("check: pf_pc ", len(pf_pc), pf_pc[0])

conns1 = []
for entry in aa_pc:
    if entry[0] < size1 and entry[1] < size2:
        conns1.append(entry)

conns2 = []
for entry in pf_pc:
    if entry[0] < size1 and entry[1] < size2:
        conns2.append(entry)

print("check: conns1 ", len(conns1), conns1[0])
print("check: conns2 ", len(conns2), conns2[0])

p1_p2_1 = sim.Projection(pop1, pop2, sim.FromListConnector(conns1),
                         receptor_type="excitatory", label="p1p21")
p1_p2_2 = sim.Projection(pop1, pop2, sim.FromListConnector(conns2),
                         receptor_type="excitatory", label="p1p22")

sim.run(10000)

sim.end()

plt.plot(list(conns2[n][0] for n in range(len(conns2))),
         list(conns2[n][1] for n in range(len(conns2))),
         'bx', markersize=2.0)
plt.plot(list(conns1[n][0] for n in range(len(conns1))),
         list(conns1[n][1] for n in range(len(conns1))),
         'ro', markersize=1.0)

plt.show()
