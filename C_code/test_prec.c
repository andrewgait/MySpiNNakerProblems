#include <sark.h>
#include <spin1_api.h>
#include <stdfix-full-iso.h>
#include <math.h>

struct double_uint {
    uint first_word;
    uint second_word;
};

union double_to_ints {
    double double_value;
    struct double_uint int_values;
};

union float_to_int {
    float float_value;
    uint int_value;
};


void print_value(double d_value) {
    union double_to_ints converter;
    converter.double_value = d_value;
    io_printf(
        IO_BUF, "0x%08x%08x",
        converter.int_values.second_word, converter.int_values.first_word);
}

void print_value_float(float d_value) {
    union float_to_int converter;
    converter.float_value = d_value;
    io_printf(IO_BUF, "0x%08x", converter.int_value);
}


void c_main() {
    vcpu_t *sark_virtual_processor_info = (vcpu_t*) SV_VCPU;
    union double_to_ints converter;
    converter.int_values.first_word =
        sark_virtual_processor_info[spin1_get_core_id()].user0;
    converter.int_values.second_word =
        sark_virtual_processor_info[spin1_get_core_id()].user1;

    double weight = 0.0878;
    double tau = 0.5;
    double timestep = converter.double_value;
    double v_rest = -65.0;
    double tau_m = 10.0;
    double c_m = 0.25;

    double decay = exp(-timestep / tau);
    double init = (1 - decay) * tau * (1.0 / timestep);
    double scale = pow(2, 32);

    double exp_tc = exp(-timestep / tau_m);
    double r_m = tau_m / c_m;

    unsigned long fract decay_fixed = (unsigned long fract) decay;
    unsigned long fract init_fixed = (unsigned long fract) init;
    accum v_rest_fixed = (accum) v_rest;
    accum exp_tc_fixed = (accum) exp_tc;
    accum r_m_fixed = (accum) r_m;

    float decay_float = (float) decay;
    float init_float = (float) init;
    float v_rest_float = (float) v_rest;
    float exp_tc_float = (float) exp_tc;
    float r_m_float = (float) r_m;

    double exact_input_prop = tau_m / (c_m *(1.0 - tau_m / tau)) * decay *
            (1.0 - exp(timestep * (1.0 / tau - 1.0 / tau_m)));
    float exact_input_float_prop = (float) exact_input_prop;
    accum exact_input_fixed_prop = (accum) exact_input_prop;

    accum weight_fixed = (accum) weight;
    float weight_float = (float) weight;

    double double_input = 0.0;
    accum fixed_input = 0.0K;
    accum exact_fixed_input = 0.0K;
    double exact_input = 0.0;
    float float_input = 0.0f;
    float exact_float_input = 0.0f;

    double double_v = v_rest;
    accum fixed_v = (accum) v_rest;
    accum exact_fixed_v = (accum) 0.0K;
    float float_v = (float) v_rest;
    double exact_v = 0.0;
    float exact_v_float = 0.0f;

    exact_input += weight;
    double_input += weight * init;
    fixed_input += weight_fixed * init_fixed;
    exact_fixed_input += weight_fixed;
    float_input += weight_float * init_float;
    exact_float_input += weight_float;

    for (uint i = 0; i < 50; i++) {
        print_value(double_input);
        io_printf(IO_BUF, "\t%k\t", fixed_input);
        print_value(exact_input);
        io_printf(IO_BUF, "\t");
        print_value_float(float_input);
        io_printf(IO_BUF, "\t");
        print_value_float(exact_float_input);
        io_printf(IO_BUF, "\t%k\t", exact_fixed_input);
        print_value(double_v);
        io_printf(IO_BUF, "\t%k\t", fixed_v);
        print_value(exact_v + v_rest);
        io_printf(IO_BUF, "\t");
        print_value_float(float_v);
        io_printf(IO_BUF, "\t");
        print_value_float(exact_v_float + v_rest_float);
        io_printf(IO_BUF, "\t%k\n", exact_fixed_v + v_rest_fixed);


        double_input *= decay;
        fixed_input *= decay_fixed;
        exact_input *= decay;
        float_input *= decay_float;
        exact_float_input *= decay_float;
        exact_fixed_input *= decay_fixed;

        double alpha_double = double_input * r_m + v_rest;
        double_v = alpha_double - (exp_tc * (alpha_double - double_v));

        accum alpha_fixed = fixed_input * r_m_fixed + v_rest_fixed;
        fixed_v = alpha_fixed - (exp_tc_fixed * (alpha_fixed - fixed_v));

        float alpha_float = float_input * r_m_float + v_rest_float;
        float_v = alpha_float - (exp_tc_float * (alpha_float - float_v));

        exact_v = (exact_v * exp_tc) + (exact_input * exact_input_prop);
        exact_v_float =
            (exact_v_float * exp_tc_float) +
            (exact_float_input * exact_input_float_prop);
        exact_fixed_v =
            (exact_fixed_v * exp_tc_fixed) +
            (exact_fixed_input * exact_input_fixed_prop);
    }
}
