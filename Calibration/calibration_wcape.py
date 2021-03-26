'''
Create model for Western Cape, South Africa
Last updated: 17 Sept, 2020
'''

# Imports
import sciris as sc
import pylab as pl
import covasim as cv
import numpy as np
import datetime as dt
#import optuna as op

# Settings for running script
do_multi = True
do_plot = True
do_save = False
start_day = '2020-03-01'

# Define population of Western Cape
total_pop = 7.0e6
pop_size = 100e3
pop_scale = int(total_pop/pop_size)

# Main calibration parameters
pop_infected = 100
beta = 0.0185 # 0.0186 works well for rand_seed = 1

# Set up pars dictionary
pars = dict(
    pop_size = pop_size,
    pop_scale = pop_scale,
    pop_infected = pop_infected,
    start_day = start_day,
    end_day='2021-03-25',
    rand_seed = 1,
    beta = beta,
    verbose = 0.1,
    location = 'south africa',
    pop_type = 'hybrid',
    rescale = True,
)

# Make a sim without parameters, just to load in the data to use in the testing intervention and to get the sim days
sim = cv.Sim(start_day=start_day, datafile="Western_Cape_em.csv")

# Add interventions:
pars['interventions'] = []

pars['interventions'] += [

        cv.clip_edges(days=['2020-03-18', '2020-06-09', '2020-07-27', '2020-08-24', '2020-11-26', '2020-12-15'], changes=[0.1, 0.8, 0.1, 0.8, 0.9, 0.1], layers=['s'], do_plot=False), # Schools closed, reopened, and closed again
        cv.change_beta(['2020-06-09', '2020-11-26', '2020-12-15'], [0.5, 0.8, 0.5], layers=['s'], do_plot=False), # Assume precautions in place after school returns

        cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01', '2020-08-17', '2020-09-20', '2020-11-11', '2020-12-18', '2021-01-04','2021-01-15'], changes=[0.65, 0.70, 0.72, 0.74, 0.92, 0.93, 0.60, 0.68, 0.72], layers=['w'], do_plot=True),
        cv.change_beta(['2020-04-10', '2020-05-01', '2020-06-01', '2020-11-01', '2020-12-18'], [0.76, 0.65, 0.43, 1.15, 0.98], layers=['w'], do_plot=False), # Assume precautions in place for workers


        cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01', '2020-08-17', '2020-09-20', '2020-11-11', '2020-12-18', '2020-12-28'], changes=[0.65, 0.70, 0.72, 0.74, 0.92, 0.93, 0.97, 0.72], layers=['c'], do_plot=False),
        cv.change_beta(['2020-04-10', '2020-05-01', '2020-06-01', '2020-11-01', '2020-12-18'], [0.76, 0.65, 0.43, 1.15, 0.98], layers=['c'], do_plot=False),  # Mandatory masks, then enforced

    ]

# 2. Testing assumptions -- no data for the first month, then using data derived from yield
pars['interventions'] += [cv.test_num(daily_tests=sim.data['new_tests'], start_day=sim.day('2020-03-05'), end_day=sim.day('2020-07-31'), test_delay=10, symp_test=30.0, quar_test=20.0, do_plot=False)]
pars['interventions'] += [cv.test_num(daily_tests=sim.data['new_tests'], start_day=sim.day('2020-08-01'), end_day=sim.day('2020-11-11'), test_delay=7, symp_test=35.0, quar_test=20.0, do_plot=False)]
pars['interventions'] += [cv.test_num(daily_tests=sim.data['new_tests'], start_day=sim.day('2020-11-12'), end_day=sim.day('2021-02-06'), test_delay=5, symp_test=30.0, quar_test=20.0, do_plot=False)]
pars['interventions'] += [cv.test_num(daily_tests=4000, start_day=sim.day('2021-02-07'), test_delay=5, symp_test=30, quar_test=20.0, do_plot=False)]


# 3. Assume some amount of contact tracing
pars['interventions'] += [cv.contact_tracing(start_day='2020-03-01',
                               trace_probs={'h': 1, 's': 0.5, 'w': 0.5, 'c': 0.1}, #'c': 0.0
                               trace_time={'h': 1, 's': 3, 'w': 7, 'c': 14}, do_plot=False)]


# Create sim and run
if __name__ == '__main__':
       
    sim = cv.Sim(pars=pars, datafile='Western_Cape_em.csv')
    if not do_multi: sim.run()

    if do_multi:
        msim = cv.MultiSim(base_sim=sim)
        msim.run(n_runs=10, reseed=True, noise=0)
        msim.reduce()




    # Plotting
    to_plot = sc.objdict({
        'Diagnoses': ['cum_diagnoses'],
        'Daily diagnoses': ['new_diagnoses'],
        'Deaths': ['cum_deaths'],
        'Daily deaths': ['new_deaths'],
        'Total infections': ['cum_infections'],
        'Cumulative tests': ['cum_tests'],
        'New infections per day': ['new_infections'],
        'New tests': ['new_tests'],
    #    'Test yield': ['test_yield'],
    #    'Number quarantined': ['n_quarantined'],
        })


    if do_plot:
        if do_multi:
            msim.plot(to_plot=to_plot, fig_args=dict(figsize=(25,20)), do_save=True, do_show=False, fig_path=f'wcape_calibration.png',
                 legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=35)
        else:
            sim.plot(to_plot=to_plot, fig_args=dict(figsize=(25,20)), do_save=True, do_show=False, fig_path=f'wcape_calibration.png',
                 legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=35)

    if do_save:
        if do_multi: msim.save(f'wcape.msim')
        else:         sim.save(f'wcape.sim')

