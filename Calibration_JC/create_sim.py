'''
File that returns a sim object for a given set of parameters
'''

# Standard packages
import os
import numpy as np
import sciris as sc
import covasim as cv

# Define the input files
epi_data_file  = 'Western_Cape.csv'
popfile_stem   = 'WC_seed'


# Generate the population filename
def get_popfile(pars):
    n_popfiles = 5
    popfile = popfile_stem + str(pars['rand_seed']%n_popfiles) + '.ppl'

    # Check that the population file exists
    if not os.path.exists(popfile):
        errormsg = f'WARNING: could not find population file {popfile}! Please regenerate first'
        raise FileNotFoundError(errormsg)

    return popfile


def define_pars(which='best'):
    ''' Define the parameter best guesses and bounds '''

    pardata = dict(
        # name              best       low       high
        beta            = [ 0.016,  0.013  ,    0.016],
        rel_severe_prob = [ 2,      1,          3],
        rel_death_prob  = [ 2,      1,          3],
        symp_prob       = [ 0.20  ,  0.05   ,   0.40],
        pop_infected    = [ 100.0   , 10.0    , 200.0],
    )

    output = {}
    for key,arr in pardata.items():
        if which == 'best':
            output[key] = arr[0]
        elif which == 'bounds':
            output[key] = arr[1:3]

    return output


def create_sim(pars=None, label=None):
    ''' Create a single simulation for further use'''
    p = sc.objdict(sc.mergedicts(define_pars(which='best'), pars))
    if 'rand_seed' not in p:
        seed = 1
        print(f'Note, could not find random seed in {pars}! Setting to {seed}')
        p['rand_seed'] = seed  # Ensure this exists

    # Define population of Western Cape
    total_pop = 7.0e6
    pop_size = 100e3
    pop_scale = int(total_pop / pop_size)

    # Basic parameters and sim creation
    pars = {'pop_size': pop_size,
            'pop_scale': pop_scale,
            'pop_type': 'hybrid',
            'location': 'south africa',
            'pop_infected': p.pop_infected,
            'beta': p.beta,
            'rel_severe_prob': p.rel_severe_prob,
            'rel_death_prob': p.rel_death_prob,
            'start_day': '2020-03-01',
            'end_day': '2020-08-29',
            'rel_imm': {'asymptomatic': 1, 'mild': 1, 'severe': 1.0},
            'rescale': True,
            'rescale_factor': 1.1,
            'verbose': p.get('verbose', 0.01),
            'rand_seed': int(p.rand_seed),
            'analyzers': cv.age_histogram(datafile='deaths_by_age.csv', edges=np.linspace(0, 85, 18))
            }

    # Create and initialize the sim
    sim = cv.Sim(pars, label=label, popfile=get_popfile(pars), load_pop=True, datafile=epi_data_file)

    interventions = []

    # Schools closed, reopened, and closed again, assume precautions in place after school returns
    interventions += [cv.clip_edges(days=['2020-03-18', '2020-06-09', '2020-07-27'], changes=[0.1, 0.8, 0.1], layers=['s'])]
    interventions += [cv.change_beta(['2020-06-09'], [0.35], layers=['s'])]

    # Workplaces closed, reopened, assume precautions in place for workers
    interventions += [cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01'], changes=[0.65, 0.70, 0.72], layers=['w'])]
    interventions += [cv.change_beta(['2020-04-10'], [0.75], layers=['w'])]

    # Mandatory masks, then enforced
    interventions += [cv.change_beta(['2020-04-10'], [0.75], layers=['c'])]

    # Testing and contact tracing
    interventions += [cv.test_prob(symp_prob=p.symp_prob, start_day='2020-03-05', test_delay=10)]
    interventions += [cv.contact_tracing(start_day='2020-03-01',
                               trace_probs={'h': 1, 's': 0.5, 'w': 0.5, 'c': 0.1},
                               trace_time={'h': 1, 's': 3, 'w': 7, 'c': 14})]

    sim['interventions'] = interventions

    # Don't show interventions in plots, there are too many
    for interv in sim['interventions']:
        interv.do_plot = False

    return sim


def run_sim(pars=None, interactive=False, sim=None, do_plot=True):
    ''' Create and run a simulation from a given set of parameters '''

    # Create and run the sim
    if sim is None:
        sim = create_sim(pars=pars)
    if not sim.results_ready:
        sim.run()

    fit = sim.compute_fit(keys=['cum_diagnoses', 'cum_deaths', 'new_diagnoses', 'new_deaths'])

    # Handle output
    if interactive:
        if do_plot:
            sim.plot()
            fit.plot()
        return sim, fit
    else:
        return fit.mismatch


if __name__ == '__main__':

    T = sc.tic()

    use_multisim  = 1

    # Settings
    reps = 5 # Set multiple runs to average over likelihood
    base_sim = create_sim()

    # Plot calibration
    if use_multisim:
        msim = cv.MultiSim(base_sim, n_runs=reps)
        msim.run(reseed=True, noise=0.0, keep_people=True, par_args={'ncpus':5})
        sims = msim.sims
        msim.plot(to_plot='overview', plot_sims=True)
        msim.reduce()
        sim = msim.base_sim
    else:
        sim = base_sim
        sim.run()
        sims = [sim]

    # Do plotting
    sim, fit = run_sim(sim=sim, interactive=True)

    sc.toc(T)