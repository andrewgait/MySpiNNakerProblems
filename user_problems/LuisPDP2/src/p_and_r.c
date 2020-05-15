#include "spin1_api.h"
#include "common-typedefs.h"
#include <data_specification.h>
#include <simulation.h>
#include <debug.h>

// ------------------------------------------------------------------------
// simulation control variables
// ------------------------------------------------------------------------
static uint32_t exit_code;
static uint32_t simulation_ticks;
static uint32_t infinite_run;
static uint32_t time;
static uint32_t timer_period;
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// report final result
// ------------------------------------------------------------------------
void done() {
    // report problems -- if any
    if (exit_code) {
        io_printf(IO_BUF, "error %u\n", exit_code);
        io_printf(IO_BUF, "simulation aborted\n");
    } else {
        io_printf(IO_BUF, "simulation OK\n");
    }
}
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// initialise simulation parameters and setup control
// ------------------------------------------------------------------------
static uint sim_init(uint32_t * timer_period) {
    // get the data specification address in SDRAM
    data_specification_metadata_t * data =
            data_specification_get_data_address();

    // check that the header is correct
    if (!data_specification_read_header(data)) {
        return 1;
    }

    // get the simulation parameters
    if (!simulation_initialise(
            data_specification_get_region(0, data),
            APPLICATION_NAME_HASH, timer_period, &simulation_ticks,
            &infinite_run, &time, 0, 0)) {
        return 1;
    }

    return 0;
}
// ------------------------------------------------------------------------

static void resume_callback(void) {
    time = UINT32_MAX;
}

// ------------------------------------------------------------------------
// timer callback: print message to iobuf
// ------------------------------------------------------------------------
void do_tick(uint tick, uint null) {
    if ((tick % 1000) == 0) {
        io_printf(IO_BUF, "p&r tick: %u\n", tick);
    }

    // check if time to finish
    if (tick >= 10000) {
        // set exit code and exit
        exit_code = 0;
        simulation_exit();

        // fall into the pause resume mode of operating
        simulation_handle_pause_resume(resume_callback);

        simulation_ready_to_read();

        return;
    }
}
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// main: initialise variables, register callbacks and run simulation
// ------------------------------------------------------------------------
void c_main() {
    // say hello,
    io_printf(IO_BUF, "p&r >>\n");

    // initialise the simulation,
    exit_code = sim_init(&timer_period);

    // check for initialisation errors,
    if (exit_code) {
        // report issues and abort simulation
        done();
        rt_error(RTE_SWERR);
    }

    // set timer tick value (in microseconds),
    spin1_set_timer_tick(timer_period);

    // register callbacks,
    spin1_callback_on(TIMER_TICK, do_tick, 0);

    // run simulation,
    //NOTE: no exit code from simulation_run()
    simulation_run();

    // report results,
    done();

    // and say goodbye
    io_printf(IO_BUF, "<< p&r\n");
}
// ------------------------------------------------------------------------
