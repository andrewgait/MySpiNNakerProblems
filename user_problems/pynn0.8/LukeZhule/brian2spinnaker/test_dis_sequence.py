
import sys
sys.setrecursionlimit(20000)

import time
import csv
import numpy as np

from copy import *
import os
import yaml
import scipy.io as sio
from brian2 import *
import brian2tools
from brian2tools import *
import pandas as pd
from scipy.sparse import rand
import brian2
import random
from deap import base
from deap import creator
from deap import tools
import json
import argparse

import pickle
from scipy.spatial.distance import euclidean

from fastdtw import fastdtw

import brian2genn
import matplotlib.pyplot as plt
from DVS import *
from PN2EN import *
random.seed = 2020
numpy.random.RandomState(seed = 2020)

import nmpi
c = nmpi.client("helloworldle")


# vkc2kc = pars[0]
# t_learning_range = pars[1]
# i_en2kc = pars[2]
# tau_i_en = pars[3]
pars =[0.1, 0.5, 3, 3, 30]


def find_index_for_distance(d, t_array):
    v = 20.0/1000
    t_l = d / v
    t_h = (d + 1) / v
    index_d = np.min(np.where((t_array >= t_l) & (t_array <= t_h)))
    return int(index_d)

def dvs2input(filename):

    ## import dvs data
    data = sio.loadmat(filename)
    idx_dvs = data['idx'][0]
    t_dvs = data['t'][0]

    ## find when the camera starts to move : density of events is larger than the time period when camrea is staying still (10>1)
    find_start_index = np.bincount(t_dvs.astype(int))
    moving = np.where(find_start_index == 7)[0]
    start = int(moving[0])
    end = int(moving[-1])
    start_t_index = np.where(t_dvs == start)[0][0]
    end_t_index = np.where(t_dvs == end)[-1][-1]

    idx_input = idx_dvs[start_t_index:end_t_index].copy()
    t_input = t_dvs[start_t_index:end_t_index].copy() - t_dvs[start_t_index]

    ##### distance = 100cm    t = d/(20cm/s)
    index_d_20 = find_index_for_distance(20,t_input)
    index_d_40 = find_index_for_distance(40,t_input)
    index_d_60 = find_index_for_distance(60 , t_input)
    index_d_80 = find_index_for_distance(80 , t_input)
    index_d_50 = find_index_for_distance(50 , t_input)
    index_d_100 = find_index_for_distance(100 , t_input)
    index_d_120 = find_index_for_distance(120 , t_input)
    index_d_150 = find_index_for_distance(150 , t_input)
    index_d_200 = find_index_for_distance(200 , t_input)
    index_d_300 = find_index_for_distance(300 , t_input)

    ### the whole route is devided into 3 parts: 1) 0-1.5m: pre-learning,  2) 1.5-2.0m: learning  2.0-4m: learning

    ##pre learning: index
    index_learning_start = 0
    index_learning_end = index_d_150

    t_value_learning_start = t_input[index_learning_start]
    t_value_learning_end = t_input[index_learning_end]

    idx_pre_learning = idx_input[0:index_learning_start].copy()
    t_pre_learning = t_input[0:index_learning_start].copy()

    idx_learn = idx_input[index_learning_start: index_learning_end].copy()
    t_learn = t_input[index_learning_start: index_learning_end].copy()

    idx_test = idx_input[index_learning_start: index_d_200].copy()
    t_test = t_input[index_learning_start: index_d_200].copy()

    t_flip = t_test.copy() * -1 + t_test[-1]
    t_flip = np.flipud(t_flip)
    idx_flip = np.flipud(idx_test.copy())

    idx_chop = np.concatenate((idx_input[index_d_100:index_d_150],idx_input[index_d_50:index_d_100],idx_input[index_learning_start:index_d_50],idx_input[index_d_150:index_d_200]))
    t_chop = np.concatenate((t_input[index_d_100:index_d_150]-t_input[index_d_100],t_input[index_d_50:index_d_100],t_input[index_learning_start:index_d_50]+t_input[index_d_100],t_input[index_d_150:index_d_200]))

    learn_input =[idx_learn , t_learn]
    test_input = [idx_test , t_test]
    chop_input = [idx_chop , t_chop]
    flip_input = [idx_flip, t_flip]
    #
    #
    # learn_input = [idx_learn , t_learn]
    # test_input = [idx_input, t_input]

    return learn_input, test_input, chop_input, flip_input



def plot_noise_EN(mb, title):
    plt.figure(figsize = (8,2))
    plt.clf()

    #ax1 = plt.subplot(211)
    #brian_plot(mb.EN_STM , label = 'before learning' , color = 'skyblue' , alpha = 0.5)
    plt.plot(mb.EN_A_STM.t/ms,mb.EN_A_STM.v[0]/mV, color = 'salmon', )
    plt.ylabel('V (mV)')
    plt.xlabel('time (ms)')
    plt.xticks([0,2500,5000,7500,10000])
   # ax2 = plt.subplot(212)
   # rate_af = mb.EN_A_RTM.smooth_rate(window = 'flat' , width = 500 * ms) / Hz
   # t = mb.EN_RTM.t / ms
   # plt.plot(t, rate_af , color = 'salmon', )
   # plt.ylabel('rate (Hz)')

    plt.savefig(fname = title+'.eps',dpi=300,format='eps')


learn_input, test_input, chop_input, flip_input = dvs2input('/home/le/Python_Plus/PycharmProjects/MBSNN0227/data/210PN_without_smooth/NB5_2020-02-19-11-19-03.mat')

mb_learn = MB_LE(dvs_input = learn_input, pars = pars)
mb_learn.run_sim()



mb_test1 = MB_LE(dvs_input = test_input, pars = pars, w_kc2kc= mb_learn.S_kc2kc_learning.w)
mb_test1.run_sim()
plot_noise_EN(mb_test1, title = 'test sequence')
#
mb_test2 = MB_LE(dvs_input = chop_input, pars = pars, w_kc2kc= mb_learn.S_kc2kc_learning.w)
mb_test2.run_sim()
plot_noise_EN(mb_test2, title = 'distort sequence')

mb_test3 = MB_LE(dvs_input = flip_input, pars = pars, w_kc2kc= mb_learn.S_kc2kc_learning.w)
mb_test3.run_sim()
plot_noise_EN(mb_test3, title = 'reverse sequence')
