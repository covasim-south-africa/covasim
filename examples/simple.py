'''
Simplest possible Covasim usage example.
'''
import sciris as sc
import covasim as cv

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
basename = f'{folder}/Gauteng_observed_data_Fin'
file_path = f'{basename}.xlsx'

pars = sc.objdict(
    pop_size     = 20e3,    # Population size
    pop_infected = 10,       # Number of initial infections
    #n_days       = 120,      # Number of days to simulate
    #rand_seed    = 1,        # Random seed
    pop_type     = 'hybrid', # Population to use -- "hybrid" is random with household, school,and work structure
)

# Optionally add an intervention
#if interv:
   # pars.interventions = cv.dynamic_pars({'beta':{'days':[45, 60], 'vals':[1, 1]}})
    #pars.interventions = cv.change_beta([0, 78],[0.006808882330503854, 0.012151798303004453])
    #pars.interventions = cv.change_beta(days=15, changes=0.633)

sim = cv.Sim(pars=pars)#, datafile = file_path, datacols = ['t', 'cum_recoveries', 'cum_infections', 'new_infections', 'cum_deaths', 'n_infectious', 'new_recoveries', 'new_deaths', 'date'])
sim.initialize()
sim.run()
sim.to_excel(res_path)
sim.plot(do_save=do_save, fig_path=fig_path)