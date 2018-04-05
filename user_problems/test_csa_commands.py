from csa import *
import cmath

@ProjectionOperator
def GvspaceToCx(p):
    w = 7.7 * cmath.log(complex(p[0]+0.33,p[1]))
    return (w.real, w.imag)


g1 = grid2d(30)
g2 = grid2d(30, x0=-7.0, xScale=8.0, yScale=8.0)

gplot2d(GvspaceToCx * g1, 900)


