#!/bin/bash
PREFIX=${HOME}/SpiNNaker

#sudo ip a add 192.168.240.50/24 dev enp0s31f6

ping -c1 192.168.240.253 || exit 1

${PREFIX}/IntroLab/sudoku/sudoku_linux -neurons_per_number 5 -ms_per_bin 100 &
sleep 1
python ${PREFIX}/IntroLab/sudoku/sudoku.py

