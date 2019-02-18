import numpy as np
from scipy.stats import poisson

# To generate a table for 8-bit PRNG
lambda_ = 1.6

i = 0
n = (1 - poisson.cdf (0, lambda_)) * (256)
while n > 0.1:
  print n
  i = i+1
  n = (1 - poisson.cdf (i, lambda_)) * (256)

# To generate a table for 32-bit PRNG
i = 0
n = (1 - poisson.cdf (0, lambda_)) * (1024*1024*1024*4)
while n > 0.1:
  print n
  i = i+1
  n = (1 - poisson.cdf (i, lambda_)) * (1024*1024*1024*4)
