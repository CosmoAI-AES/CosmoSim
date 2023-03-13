#! /usr/bin/env python3

"""
Generate the 50.txt file containing expressions for alpha and beta
for the SIS model in Roulettes.

Usage: `python3 Amplitudes_gen.py [n [nproc]]`

- `n` is the maximum number of terms
- `nproc` is the number of threads
"""

import multiprocessing as mp
import sys
import time

from sympy import simplify, symbols, sqrt, diff, factor

def listener(fn,q):
    '''Listens for messages on the Queue q and writes to file `fn`. '''
    print( "Listener starts with file ", fn ) 
    with open(fn, 'w') as f:
        print( "Opened file", fn ) 
        while 1:
            # print(f'Jobs running: {}')
            m = q.get()
            # print("got write job:", m)
            if m == 'kill':
                print("Done")
                break
            f.write(str(m) + '\n')
            f.flush()
        print( "File writer terminated", fn ) 
    if hit_except: print( "Failed to open file ", fn )

def func(n, m, s, alpha, beta, x, y, g, q):
    """
    Generate the amplitudes for one fixed sum $m+s$.
    This is done by recursion on s and m.
    """
    print(f'm: {m} s: {s}')# alpha: {alpha} beta: {beta}')
    while s > 0 and m < n:
        m += 1
        s -= 1
        c = ((m + 1.0) / (m + 1.0 - s) * (1.0 + (s != 0.0)) / 2.0)
        # start calculate
        alpha_ = factor(c * (diff(alpha, x) + diff(beta, y)))
        beta_ = factor(c * (diff(beta, x) - diff(alpha, y)))
        alpha, beta = alpha_, beta_
        print(f'm: {m} s: {s}')# alpha: {alpha} beta: {beta} c: {c}')
        # print("gen write job")
        res = f'{m}:{s}:{alpha}:{beta}'
        # print(f'{m}, {s} Done')
        q.put(res)

def main():

    global num_processes

    # Argument 1 is the number of amplitudes
    if len(sys.argv) < 2:
       n = 50
    else:
       n = int(sys.argv[1])
    # Argument 2 is the number of threads to use
    if len(sys.argv) < 3:
       nproc = n
    else:
       nproc = int(sys.argv[2])
    
    # The filename is generated from the number of amplitudes
    fn = str(n) + '.txt'

    start = time.time()


    # psi is the lens potential
    # g is the Einstein radius and (x,y) coordinates in the lens plane
    x, y = symbols('x, y', real=True)
    g = symbols("g", positive=True, real=True)
    psi = - g * sqrt(x ** 2 + y ** 2)

    # Must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()

    with mp.Pool(processes=nproc) as pool:

        # use a single, separate process to write to file 
        pool.apply_async(listener, (fn,q,))

        jobs = []
        for m in range(0, n+1):

            s = m + 1

            if m == 0:
                # This is the base case (m,s)=(0,1) of the outer recursion
                alpha = factor(diff(psi, x))
                beta = factor(diff(psi, y))
            else:
                # This is the base case (m+1,s+1) of the inner recursion
                c = (m + 1.0) / (m + s + 1.0) 
                alpha_ = factor(c * (diff(alpha, x) - diff(beta, y)))
                beta_ = factor(c * (diff(beta, x) + diff(alpha, y)))
                alpha, beta = alpha_, beta_


            res = f'{m}:{s}:{alpha}:{beta}'
            q.put(res)

            job = pool.apply_async(func, (n, m, s, alpha, beta, x, y, g, q))
            jobs.append(job)

        # collect results from the workers through the pool result queue
        for job in jobs:
            job.get()

    # Now we are done, kill the listener
    q.put('kill')
    print( "Issued kill signal" )
    pool.close()
    print( "Pool closed" )
    pool.join()
    print( "Pool joined" )

    print( "Time spent:", time.time() - start)

if __name__ == "__main__":
   main()