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
basename = f'{folder}/SA_observed_data_Fin'
file_path = f'{basename}.xlsx'

pars = sc.objdict(
    pop_size     = 1500e3,    # Population size
    pop_infected = 10,       # Number of initial infections
    #n_days       = 120,      # Number of days to simulate
    #rand_seed    = 1,        # Random seed
    pop_type     = 'hybrid', # Population to use -- "hybrid" is random with household, school,and work structure
    start_day = '2020-03-05' , # First day of the simulation
    end_day = '2020-06-30' , # Last day of the simulation
)

interventions = [
    cv.clip_edges([18, 45, 60], [0.0, 0.3, 0.3], layers='s'), # Close schools
    #cv.clip_edges(start_day= '2020-03-26' , end_day= '2020-04-10' , change={ 'w' : 0.7 , 'c' : 0.7 }), # Reduce work and community
    #cv.clip_edges(start_day= '2020-04-10' , end_day= '2020-05-05' , change={ 'w' : 0.3 , 'c' : 0.3 }), # Reduce both further
    #cv.clip_edges(start_day= '2020-05-05' , end_day= None , change={ 'w' : 0.8 , 'c' : 0.8 }), # Partially reopen
    #cv.test_prob(start_day= '2020-05-20' , symp_prob= 0.10 , symp_quar_prob= 0.8 , test_delay= 2 ), # Testing
    #cv.contact_tracing(start_day= '2020-04-20' , trace_probs=trace_probs, trace_time=trace_time) # Contact tracing
    ]


# Optionally add an intervention
# if interv:
   # # pars.interventions = cv.dynamic_pars({'beta':{'days':[45, 60], 'vals':[1, 1]}})
    # pars.interventions = cv.change_beta([45, 60],[0.3, 0.3])
    # #pars.interventions = cv.change_beta(days=15, changes=0.633)

sim = cv.Sim(pars=pars, interventions=interventions, datafile = file_path, datacols = ['t', 'cum_recoveries', 'cum_infections', 'new_infections', 'cum_deaths', 'n_infectious', 'new_recoveries', 'new_deaths', 'date'])
sim.initialize()
sim.run()
sim.to_excel(res_path)
sim.plot(do_save=do_save, fig_path=fig_path)