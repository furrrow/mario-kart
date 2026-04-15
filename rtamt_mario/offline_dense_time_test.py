#!/usr/bin/env python
import sys
import rtamt

def monitor(data1):
    # # #
    #
    # Example (a) - output robustness
    #
    # # #
    spec = rtamt.StlDenseTimeSpecification(semantics=rtamt.Semantics.OUTPUT_ROBUSTNESS)
    spec.name = 'Example 1'
    spec.declare_var('req', 'float')
    spec.declare_var('gnt', 'float')
    spec.declare_var('out', 'float')
    spec.set_var_io_type('req', 'input')
    spec.set_var_io_type('gnt', 'output')
    spec.spec = 'out = ((req>=3) implies (eventually[0:3](gnt>=3)))'
    try:
        spec.parse()
    except rtamt.RTAMTException as err:
        print('RTAMT Exception: {}'.format(err))
        sys.exit()

    rob = spec.evaluate(['req', data1['req']], ['gnt', data1['gnt']])

    print('Example (a) - output robustness: {}'.format(rob))

if __name__ == '__main__':
    data1 = {
        'time': [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (4.0, 4.0)],
        'req': [(0, 0.0), (1, 4.0), (2, 0.0), (3, 0.0), (4, 0.0)],
        'gnt': [(0, 0.0), (1, 0.0), (2, 4.0), (3, 0.0), (4, 0.0)]
    }

    monitor(data1)
