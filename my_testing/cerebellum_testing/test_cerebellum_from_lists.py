# Trying to reproduce from-list related cerebellum problems in a simpler format

# Population sizes for "loaded" cerebellum model:

# golgi           ->        219 neurons
# glomerulus      ->       7073 neurons (SSA)
# granule         ->      88158 neurons
# purkinje        ->         69 neurons
# basket          ->        603 neurons
# stellate        ->        603 neurons
# dcn             ->         12 neurons

# Problems appear to be related to golgi and purkinjie in that instance

# purkinjie connections come from aa (granule exc), bc (basket inh),
# pf (granule exc), sc (stellate inh)

import numpy as np
import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)

stellate = sim.Population(603, sim.IF_cond_exp, label="stellate")
purkinjie = sim.Population(69, sim.IF_cond_exp, label="purkinjie")
basket = sim.Population(603, sim.IF_cond_exp, label="basket")
granule = sim.Population(88158, sim.IF_cond_exp, label="granule")
golgi = sim.Population(219, sim.IF_cond_exp, label="golgi")
dcn = sim.Population(12, sim.IF_cond_exp, label="dcn")
spikeArray = {'spike_times': [[1]]}
glomerulus = sim.Population(
    7073, sim.SpikeSourceArray(**spikeArray), label="glomerulus")

global_n_neurons_per_core = 64

stellate.set_max_atoms_per_core(global_n_neurons_per_core)
basket.set_max_atoms_per_core(global_n_neurons_per_core)
purkinjie.set_max_atoms_per_core(1)
granule.set_max_atoms_per_core(global_n_neurons_per_core)
golgi.set_max_atoms_per_core(global_n_neurons_per_core)
dcn.set_max_atoms_per_core(global_n_neurons_per_core)
glomerulus.set_max_atoms_per_core(global_n_neurons_per_core)

# Load in projections from files
aa_goc = np.loadtxt("conn_aa_goc.txt")
print("check: aa_goc ", len(aa_goc), aa_goc[0])
aa_pc = np.loadtxt("conn_aa_pc.txt")
print("check: aa_pc ", len(aa_pc), aa_pc[0])
bc_pc = np.loadtxt("conn_bc_pc.txt")
print("check: bc_pc ", len(bc_pc), bc_pc[0])
gj_bc = np.loadtxt("conn_gj_bc.txt")
print("check: gj_bc ", len(gj_bc), gj_bc[0])
gj_goc = np.loadtxt("conn_gj_goc.txt")
print("check: gj_goc ", len(gj_goc), gj_goc[0])
gj_sc = np.loadtxt("conn_gj_sc.txt")
print("check: gj_sc ", len(gj_sc), gj_sc[0])
glom_dcn = np.loadtxt("conn_glom_dcn.txt")
print("check: glom_dcn ", len(glom_dcn), glom_dcn[0])
glom_goc = np.loadtxt("conn_glom_goc.txt")
print("check: glom_goc ", len(glom_goc), glom_goc[0])
glom_grc = np.loadtxt("conn_glom_grc.txt")
print("check: glom_grc ", len(glom_grc), glom_grc[0])
goc_grc = np.loadtxt("conn_goc_grc.txt")
print("check: goc_grc ", len(goc_grc), goc_grc[0])
pc_dcn = np.loadtxt("conn_pc_dcn.txt")
print("check: pc_dcn ", len(pc_dcn), pc_dcn[0])
pf_bc = np.loadtxt("conn_pf_bc.txt")
print("check: pf_bc ", len(pf_bc), pf_bc[0])
pf_goc = np.loadtxt("conn_pf_goc.txt")
print("check: pf_goc ", len(pf_goc), pf_goc[0])
pf_pc = np.loadtxt("conn_pf_pc.txt")
print("check: pf_pc ", len(pf_pc), pf_pc[0])
pf_sc = np.loadtxt("conn_pf_sc.txt")
print("check: pf_sc ", len(pf_sc), pf_sc[0])
sc_pc = np.loadtxt("conn_sc_pc.txt")
print("check: sc_pc ", len(sc_pc), sc_pc[0])

aa_goc_proj = sim.Projection(granule, golgi,
                             sim.FromListConnector(aa_goc),
                             receptor_type="excitatory",
                             label="aa_goc")
aa_pc_proj = sim.Projection(granule, purkinjie,
                            sim.FromListConnector(aa_pc),
                            receptor_type="excitatory",
                            label="aa_pc")
bc_pc_proj = sim.Projection(basket, purkinjie,
                            sim.FromListConnector(bc_pc),
                            receptor_type="inhibitory",
                            label="bc_pc")
gj_bc_proj = sim.Projection(basket, basket,
                            sim.FromListConnector(gj_bc),
                            receptor_type="inhibitory",
                            label="gj_bc")
gj_goc_proj = sim.Projection(golgi, golgi,
                             sim.FromListConnector(gj_goc),
                             receptor_type="inhibitory",
                             label="gj_goc")
gj_sc_proj = sim.Projection(stellate, stellate,
                            sim.FromListConnector(gj_sc),
                            receptor_type="inhibitory",
                            label="gj_sc")
glom_dcn_proj = sim.Projection(glomerulus, dcn,
                               sim.FromListConnector(glom_dcn),
                               receptor_type="excitatory",
                               label="glom_dcn")
glom_goc_proj = sim.Projection(glomerulus, golgi,
                               sim.FromListConnector(glom_goc),
                               receptor_type="excitatory",
                               label="glom_goc")
glom_grc_proj = sim.Projection(glomerulus, granule,
                               sim.FromListConnector(glom_grc),
                               receptor_type="excitatory",
                               label="glom_grc")
goc_grc_proj = sim.Projection(golgi, granule,
                              sim.FromListConnector(goc_grc),
                              receptor_type="inhibitory",
                              label="goc_grc")
pc_dcn_proj = sim.Projection(purkinjie, dcn,
                             sim.FromListConnector(pc_dcn),
                             receptor_type="inhibitory",
                             label="pc_dcn")
pf_bc_proj = sim.Projection(granule, basket,
                            sim.FromListConnector(pf_bc),
                            receptor_type="excitatory",
                            label="pf_bc")
pf_goc_proj = sim.Projection(granule, golgi,
                             sim.FromListConnector(pf_goc),
                             receptor_type="excitatory",
                             label="pf_goc")
pf_pc_proj = sim.Projection(granule, purkinjie,
                            sim.FromListConnector(pf_pc),
                            receptor_type="excitatory",
                            label="pf_pc")
pf_sc_proj = sim.Projection(granule, stellate,
                            sim.FromListConnector(pf_sc),
                            receptor_type="excitatory",
                            label="pf_sc")
sc_pc_proj = sim.Projection(stellate, purkinjie,
                            sim.FromListConnector(sc_pc),
                            receptor_type="inhibitory",
                            label="sc_pc")

sim.run(10000)

sim.end()



