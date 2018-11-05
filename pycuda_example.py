#!/usr/bin/env python

import numpy
import pycuda.driver as cuda
# MUST initialization, context creation and cleanup
import pycuda.autoinit
from pycuda.compiler import SourceModule


def main():
    # nVida devices only support single precision
    a = numpy.random.randn(4, 4).astype(numpy.float32)
    # allocate memory on the device
    a_gpu = cuda.mem_alloc(a.nbytes)
    print('allocate %d byte at gpu' % a.nbytes)
    print(a_gpu)
    # transfer the data to the GPU
    cuda.memcpy_htod(a_gpu, a)



if __name__ == '__main__':
    main()

