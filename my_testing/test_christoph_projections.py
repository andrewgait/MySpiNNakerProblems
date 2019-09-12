import pyNN.spiNNaker as p

n_pops = 100
n_neurons = 2

p.setup(timestep=1.0)

weight = 0.015
delay = 1.0

single_projection = False

pop = p.Population(n_pops * n_neurons, p.IF_cond_exp, {}, label="pop")

conns = list()

for pop_src in xrange(0, n_pops):
    id_src = pop_src * n_neurons
    for pop_tar in xrange(0, n_pops):
        id_tar = pop_tar * n_neurons
        if(id_src == id_tar):
            continue
        for n_src in xrange(0, n_neurons):
            for n_tar in xrange(0, n_neurons):
                conns.append([id_src + n_src, id_tar + n_tar, weight, delay])
        if not single_projection:
            p.Projection(pop, pop, p.FromListConnector(conns), receptor_type="inhibitory")
            print(conns)
            conns= list()

for i in range(len(conns)):
    print(conns[i])

if single_projection:
    p.Projection(pop, pop,  p.FromListConnector(conns), receptor_type="inhibitory")


p.run(100)
p.end()

