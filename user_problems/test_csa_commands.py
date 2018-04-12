from csa import *
import cmath

# Testing CSA commands, from https://github.com/INCF/csa/blob/master/README.md

# To display a finite portion of the corresponding connectivity matrix, type:

show (full)

# One-to-one connectivity (where source node 0 is connected to target node 0,
# source 1 to target 1 etc) is represented by the mask oneToOne:

show (oneToOne)

# The default portion displayed by "show" is (0, 29) x (0, 29).
# (0, 99) x (0, 99) can be displayed using: ::

show (oneToOne, 100, 100)

# If source and target set is the same, oneToOne describes self-connections.
# We can use CSA to compute the set of connections consisting of all possible
# connections except for self-connections using the set difference operator "-":

show (full - oneToOne)

# Finite connection sets can be represented using either lists of connections,
# with connections represented as tuples:

show ([(22, 7), (8, 23)])

# or using the Cartesian product of intervals:

show (cross (range (10), range (20)))

# We can form a finite version of the infinite oneToOne by taking the intersection "*" with a finite connection set: ::

c = cross (range (10), range (10)) * oneToOne
show (c)

# Finite connection sets can be tabulated:

tabulate (c)

# In Python, finite connection sets provide an iterator interface:

for x in cross (range (10), range (10)) * oneToOne:
    print x

# Random connectivity and the block operator
# Connectivity where the existence of each possible connection is determined by
# a Bernoulli trial with probability p is expressed with the random mask
# random (p), e.g.:

show (random (0.5))

# The block operator expands each connection in the operand into a rectangular
# block in the resulting connection matrix, e.g.: ::

show (block (5,3) * random (0.5))

# Note that "*" here means operator application. There is also a quadratic
# version of the operator:

show (block (10) * random (0.7))

# Using intersection and set difference, we can now formulate a more
# complex mask:

show (block (10) * random (0.7) * random (0.5) - oneToOne)

@ProjectionOperator
def GvspaceToCx(p):
    w = 7.7 * cmath.log(complex(p[0]+0.33,p[1]))
    return (w.real, w.imag)


@ProjectionOperator
def GcxToVspace(p):
    c = cmath.exp(complex(p[0], p[1])/7.7)-0.33
    return (c.real, c.imag)

# Geometry
#
# In CSA, the basic tool to handle distance dependent connectivity is metrics.
# Metrics are value sets d (i, j). Metrics can be defined through geometry
# functions. A geometry function maps an index to a position. We can, for
# example, assign a random position in the unit square to each index:


g = random2d(900)
gplot2d(g, 900)

g = grid2d(30)
gplot2d(g, 900)
d = euclidMetric2d(g)
r = 0.2
c = disc(r)*d
gplotsel2d(g, c, [221, 484, 752], range(900))
print "disc(0.2)*metric on grid2d(30): "
for x in c * cross([221, 484, 752], range(900)):
    print x

g1 = grid2d(30)
g2 = grid2d(30, x0=-7.0, xScale=8.0, yScale=8.0)

gplot2d(GvspaceToCx * g1, 900)

c = disc(0.3)*euclidMetric2d(g1, GcxToVspace * g2)

gplotsel2d(g2, c, [282], range(900))
gplotsel2d(GvspaceToCx * g1, c, [282], range(900))

print "disc(0.3)*metric on curved projection from one grid to another: "
for x in c * cross([282], range(900)):
    print x
