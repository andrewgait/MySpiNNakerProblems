
# SpiNNaker environment setup

   The home of all SpiNNaker resources is the [Spinnaker Github.io] page.  This
   setup roughly follows the instructions on the [devenv] page on a Ubuntu
   16.04.3 LTS.

   [Spinnaker Github.io]: http://spinnakermanchester.github.io/
   [devenv]: http://spinnakermanchester.github.io/development/devenv.html

## Compiler Setup

   To compile everything from source we need libraries, perl and a
   cross-compiling GCC.

    sudo apt-get install libc6-i386
    sudo apt-get install perl perl-tk libterm-readline-gnu-perl

   We also need the cross compiler for the SpiNNaker ARM architecture. This is
   available on [launchpad-gcc-arm]. To just download the binaries do the
   following:

    wget "https://launchpad.net/gcc-arm-embedded/5.0/5-2016-q3-update/+download/gcc-arm-none-eabi-5_4-2016q3-20160926-linux.tar.bz2"
    tar -xvjf gcc-arm-none-eabi-5_4-2016q3-20160926-linux.tar.bz2

   [launchpad-gcc-arm]: https://launchpad.net/~team-gcc-arm-embedded/+archive/ubuntu/ppa

## Python Dependencies

   The required packages can be installed as described in the tutorial, but if
   you have one of the [Conda] flavours installed ([Miniconda], [Anaconda]) you
   can easily set up a conda environment with:

    conda env create -n spi -f=environment.yaml

   [Conda]: https://conda.io/
   [Miniconda]: https://conda.io/miniconda.html
   [Anaconda]: https://anaconda.org/


## SpiNNaker Source Code

### Github Repositories

   For the developer versions of the SpiNNaker software packages clone all
   required repositories from github. Check the `getRepositories` file and
   comment either `\*7` or `\*8` versions. *This has to be the same as your
   version of PyNN.*

    bash getRepositories


### sPyNNaker Python packages

   Install the python packages into the user environment.
   Edit the following file and uncomment `\*7` or `\*8` as above.

   **NOTE:** This installs to ~/.local/lib and *not* into the conda environment. (FIXME)

    ./SupportScripts/setup.sh
    cd spalloc
    python setup.py develop --no-deps --user
    cd spalloc_server
    python setup.py develop --no-deps --user


## Shell Environment

   To actually use the software and make all libraries available to the
   programs some environment variables need to be set up. Edit the `setup.sh`
   to suite your setup then load it with:

    source setup.sh

   Whenever you (re-)start working in a new terminal, this setup needs to be
   done first. Alternatively you could add the contents of setup.sh to your
   `~/.bashrc`.


## Build C code

   The C components have to be built in a specific order. To compile all
   downloaded components call

    bash SupportScripts/automatic_make.sh


## PyNN Setup

   To register sPyNNaker with the pyNN installation, the setup script writes
   the spynnaker `__init__()` into the pyNN module path.

    python sPyNNaker8/spynnaker8/setup-pynn.py


## sPyNNaker configuration file

   If the config file is not created automatically copy a file with some defaults:

    cp ./sPyNNaker/spynnaker/pyNN/spynnaker.cfg ~/.spynnaker.cfg 

   or

    cp spynnaker.cfg ~/.spynnaker.cfg


## Network setup


   Connect the board and setup your IP address to be in the 192.168.240.0/24
   network. You can do this in System Settings... or on the console with:

    sudo ip a add 192.168.240.50/24 dev enp0s31f6

   To test the connection ping the board

    ping 192.168.240.253



# Examples

## VA Benchmark

   A test of the board resulting in a dot-display with neuron spike times is
   available in the `PyNN8Examples/examples/` folder.

    python PyNN8Examples/examples/va_benchmark.py

## Sudoku Example

   The SpiNNaker board can be used to let the neurons solve a Sudoku puzzle.
   The description of the exercise is in the IntroLab/ and on [sudoku-googledoc]
   This example needs the pyopengl

    python IntroLab/sudoku/sudoku.py 

   Bug fix:
    line 78: p.setup(timestep=1.0, min_delay=1.0)

   In case of problems with libglut in conda...

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/terhorst/miniconda3/envs/spi/lib/
    ./IntroLab/sudoku/sudoku_linux -neurons_per_number 5 -ms_per_bin 100 &
    sleep 1   # this might not be necessary
    python IntroLab/sudoku/sudoku.py

   [sudoku-googledoc]: https://docs.google.com/document/d/1yfjEShsG0gvnGBnkCrEjNHtPJbb6Ff8bX3pKl78KiJ4

# Debugging

## Connection to the board

   As described above you can test the connection to the board with a simple `ping`.

    ping 192.168.240.253

   If this is not successful you should

   * check your cables
   * check if the network LEDs on the board are on
   * reset the board
   * verify your network setup


## What's happening on the chips?


   To communicate with the chips via a simple command line interface start
   `ybug`.  You can run `ps` on the processors to see what is going on. To
   select a specific processor use the `sp <x> <y>` command with `<x>` and
   `<y>` being the 'co-ordinates' of the chip you want to talk to.

    $ ybug 192.168.240.253
    # ybug - version 3.1.0
    192.168.240.253:0,0,0 > ps
    Core State  Application       ID   Running  Started
    ---- -----  -----------       --   -------  -------
      0  RUN    scamp-3            0   0:44:56  13 Sep 15:01  SWC 5
      1  IDLE   sark               0   0:05:16  13 Sep 15:41 
      2  IDLE   sark               0   0:05:16  13 Sep 15:41 
      3  IDLE   sark               0   0:05:16  13 Sep 15:41 
      4  IDLE   sark               0   0:05:16  13 Sep 15:41 
      5  IDLE   sark               0   0:05:16  13 Sep 15:41 
      6  IDLE   sark               0   0:05:16  13 Sep 15:41 
      7  IDLE   sark               0   0:05:16  13 Sep 15:41 
      8  IDLE   sark               0   0:05:16  13 Sep 15:41 
      9  IDLE   sark               0   0:05:16  13 Sep 15:41 
     10  IDLE   sark               0   0:05:16  13 Sep 15:41 
     11  IDLE   sark               0   0:05:16  13 Sep 15:41 
     12  IDLE   sark               0   0:05:16  13 Sep 15:41 
     13  IDLE   sark               0   0:05:16  13 Sep 15:41 
     14  IDLE   sark               0   0:05:16  13 Sep 15:41 
     15  IDLE   sark               0   0:05:16  13 Sep 15:41 
     16  IDLE   sark               0   0:05:16  13 Sep 15:41 
     17  IDLE   sark               0   0:05:16  13 Sep 15:41 
    192.168.240.253:0,0,0 > sp 0 1
    192.168.240.253:0,1,0 > ps
    Core State  Application       ID   Running  Started
    ---- -----  -----------       --   -------  -------
      0  RUN    scamp-3            0   0:44:56  13 Sep 15:01  SWC 5
      1  IDLE   sark               0   0:05:16  13 Sep 15:41 
      2  IDLE   sark               0   0:05:16  13 Sep 15:41 
    ...
