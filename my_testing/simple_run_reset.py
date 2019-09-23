import spynnaker8 as sim

sim.setup(1.0)
pop = sim.Population(1, sim.IF_curr_exp, {}, label="pop")
pop.set(i_offset=1.0)
pop.record(["v"])

for i in range(1):
    print('**************** LOOP ', i)
    pop.initialize(v=-64.0)
    pop.set(v_thresh=-55.0)
    sim.run(15)
    v1 = pop.spinnaker_get_data('v')

    sim.reset()
    pop.initialize(v=-62.0)
    pop.set(v_thresh=-52.0)
    sim.run(15)
    v2 = pop.spinnaker_get_data('v')

    sim.reset()
    pop.initialize(v=-63.0)
    pop.set(v_thresh=-50.0)
    pop.set(i_offset=2.0)
    sim.run(15)
    v3 = pop.spinnaker_get_data('v')

    pop.initialize(v=-61.0)
    pop.set(v_thresh=-54.0)
    sim.run(15)
    v4 = pop.spinnaker_get_data('v')
    v = pop.get_data('v')

sim.end()

print("v1: ", v1)
print("v2: ", v2)
print("v3: ", v3)
print("v4: ", v4)
print("v: ", v)
print("v segment 0 [0]", v.segments[0].filter(name='v')[0][0])
print("v segment 1 [0]", v.segments[1].filter(name='v')[0][0])
print("v segment 2 [0]", v.segments[2].filter(name='v')[0][0])
print("v segment 2 [15]", v.segments[2].filter(name='v')[0][15])

print('len segment 0', len(v.segments[0].filter(name='v')[0]))

print("v segment 1 [15]", v.segments[1].filter(name='v')[0][15])



