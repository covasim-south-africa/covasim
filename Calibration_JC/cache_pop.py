'''
Pre-generate the population.
'''

import psutil
import sciris  as sc
import covasim as cv

pop_size = 100e3

def cache_populations(seed=0, popfile=None):
    ''' Pre-generate the population '''

    pars = sc.objdict(
        pop_size = pop_size,
        pop_type = 'hybrid',
        location = 'south africa',
        rand_seed = seed,
    )

    if popfile is None:
        popfile = f'WC_seed{pars.rand_seed}.ppl'

    T = sc.tic()
    print(f'Making "{popfile}"...')
    sim = cv.Sim(pars)
    cv.make_people(sim, popfile=popfile, save_pop=True)
    sc.toc(T)

    print('Done')
    return


if __name__ == '__main__':

    seeds = [0,1,2,3,4] # NB, each one takes 8 GB of RAM! -- split up 0-4 in pieces
    ram = psutil.virtual_memory().available/1e9
    required = pop_size/225e3*len(seeds)
    if required < ram:
        print(f'You have {ram} GB of RAM, and this is estimated to require {required} GB: you should be fine')
    else:
        raise ValueError(f'You have {ram:0.2f} GB of RAM, but this is estimated to require {required} GB')
    sc.parallelize(cache_populations, iterarg=seeds) # Run them in parallel