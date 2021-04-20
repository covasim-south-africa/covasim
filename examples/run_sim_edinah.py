'''
Simple script for running Covasim
'''

import sciris as sc
import covasim as cv

# Run options
do_plot = 1
do_save = 1
verbose = 1
interv  = 1

# Set filename if saving
version  = 'v0'
date     = '2020apr17'
folder   = 'results_simple_run'
basename = f'{folder}/covasim_run_{date}_{version}'
fig_path = f'{basename}.png'
res_path = f'{folder}/covasim_results_{date}_{version}.xlsx'

folder   = 'data'
basename = f'{folder}/western_cape_observed_data_august'
file_path = f'{basename}.xlsx'

# Define population of Western Cape
total_pop = 7.0e6
pop_size = 100e3
pop_scale = int(total_pop / pop_size)


# Configure the sim -- can also just use a normal dictionary
pars = sc.objdict(
    beta         = 0.013052488846365529,
    pop_size     = 7.0e4,    # Population size
    pop_scale    = 70.0,
    pop_infected = 184.5038352935306,       # Number of initial infections
    #n_days       = ,      # Number of days to simulate
    rand_seed    = 1,   # Random seed
    rel_severe_prob = 2.9323176315383948, 
    rel_death_prob = 2.9349298722306063, 
    #symp_prob = 0.2621749298080359, 
    pop_type     = 'hybrid', # Population to use -- "hybrid" is random with household, school,and work structure
    start_day = '2020-03-01' , # First day of the simulation
    end_day = '2020-08-29' ,
)

interventions = [

    # Schools closed, reopened, and closed again, assume precautions in place after school returns
    cv.clip_edges(days=['2020-03-18', '2020-06-09', '2020-07-27'], changes=[0.1, 0.8, 0.1], layers=['s']),
    cv.change_beta(['2020-06-09'], [0.35], layers=['s']),

    # Workplaces closed, reopened, assume precautions in place for workers
    cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01'], changes=[0.65, 0.70, 0.72], layers=['w']),
    cv.change_beta(['2020-04-10'], [0.75], layers=['w']),

    # Mandatory masks, then enforced
    cv.change_beta(['2020-04-10'], [0.75], layers=['c']),

    # Testing and contact tracing
    cv.test_prob(symp_prob=0.2621749298080359, start_day='2020-03-05', test_delay=10),
    cv.contact_tracing(start_day='2020-03-01',
                               trace_probs={'h': 1, 's': 0.5, 'w': 0.5, 'c': 0.1},
                               trace_time={'h': 1, 's': 3, 'w': 7, 'c': 14}),]

# Optionally add an intervention
#if interv:
 #   pars.interventions = cv.change_beta(days=45, changes=0.5)

# Make, run, and plot the sim
sim = cv.Sim(pars=pars, interventions=interventions, datafile = file_path, datacols = ['t', 'cum_recoveries', 'cum_infections', 'new_infections', 'cum_deaths', 'n_infectious', 'new_recoveries', 'new_deaths', 'date'])
sim.initialize()
sim.run(verbose=verbose)
sim.to_excel(res_path)
if do_plot:
    sim.plot(do_save=do_save, fig_path=fig_path)
