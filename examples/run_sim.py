'''
Simple script for running Covasim
'''

import sciris as sc
import covasim as cv

# Run options
do_plot = 1
verbose = 1
interv  = 1

# Set filename if saving
version  = 'v0'
date     = '2020apr06'
folder   = 'results'
basename = f'{folder}/covasim_run_{date}_{version}'
fig_path = f'{basename}.png'
res_path = f'{folder}/covasim_results_{date}_{version}.xlsx'

folder_data   = 'data'
basename_data = f'{folder_data}/SA_observed_data_Fin'
file_path = f'{basename_data}.xlsx'

# Configure the sim -- can also just use a normal dictionary
pars = sc.objdict(
    pop_size     = 10000,    # Population size
    pop_infected = 10,       # Number of initial infections
    n_days       = 120,      # Number of days to simulate
    rand_seed    = 1,        # Random seed
    pop_type     = 'hybrid', # Population to use -- "hybrid" is random with household, school,and work structure
)

# Optionally add an intervention
if interv:
    pars.interventions = cv.change_beta(days=45, changes=0.5)

# Make, run, and plot the sim
sim = cv.Sim(pars=pars, datafile = file_path, datacols = ['t', 'cum_recoveries', 'cum_infections', 'new_infections', 'cum_deaths', 'n_infectious', 'new_recoveries', 'new_deaths', 'date'])
sim.initialize()
sim.run(verbose=verbose)
if do_plot:
    sim.plot()
