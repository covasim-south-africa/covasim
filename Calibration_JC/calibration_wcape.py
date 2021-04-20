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
plot_hist = True
start_day = '2020-03-01'

# Define population of Western Cape
total_pop = 7.0e6
pop_size = 100e3
pop_scale = int(total_pop/pop_size)

# Main calibration parameters
pop_infected = 100
beta = 0.0162 # 0.0186 works well for rand_seed = 1

# Set up pars dictionary
pars = dict(
    pop_size = pop_size,
    pop_scale = pop_scale,
    pop_infected = pop_infected,
    start_day = start_day,
    end_day='2021-01-31',
    rand_seed = 1,
    beta = beta,
    verbose = 0.1,
    location = 'south africa',
    pop_type = 'hybrid',
    rescale = True,
    iso_factor = dict(h=0.5, s=0.4, w=0.4, c=0.5), # default: dict(h=0.3, s=0.1, w=0.1, c=0.1)
    quar_factor= dict(h=0.9, s=0.5, w=0.5, c=0.7), # default: dict(h=0.6, s=0.2, w=0.2, c=0.2)
    rel_severe_prob = 2., # People are more/less likely to develop severe infection
    rel_death_prob=2.,  # People are more/less likely to die after developing critical illness
    rel_imm={'asymptomatic': 1, 'mild': 1, 'severe': 1.0},
    analyzers = cv.age_histogram(datafile='deaths_by_age.csv', edges=np.linspace(0, 85, 18))
)

# Make a sim without parameters, just to load in the data to use in the testing intervention and to get the sim days
sim = cv.Sim(start_day=start_day, datafile="Western_Cape_oct.csv")

# Add interventions:
pars['interventions'] = []

pars['interventions'] += [

        cv.clip_edges(days=['2020-03-18', '2020-06-09', '2020-07-27', '2020-08-24'], changes=[0.1, 0.8, 0.1, 0.8], layers=['s'], do_plot=False), # Schools closed, reopened, and closed again
        cv.change_beta(['2020-06-09'], [0.35], layers=['s'], do_plot=False), # Assume precautions in place after school returns

        cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01', '2020-08-17', '2020-09-20'], changes=[0.65, 0.70, 0.72, 0.74, 0.92], layers=['w'], do_plot=True),
        cv.change_beta(['2020-04-10'], [0.75], layers=['w'], do_plot=False), # Assume precautions in place for workers

#        cv.clip_edges(days=['2020-03-27', '2020-05-01', '2020-06-01', '2020-08-17', '2020-09-20', '2020-11-11', '2020-12-18', '2020-12-28'], changes=[0.65, 0.70, 0.72, 0.74, 0.92, 0.93, 0.97, 0.72], layers=['c'], do_plot=False),
        cv.change_beta(['2020-04-10'], [0.75], layers=['c'], do_plot=False),  # Mandatory masks, then enforced

    ]


pars['interventions'] += [
    cv.test_prob(symp_prob=0.060, start_day='2020-03-05', end_day='2020-07-31', test_delay=10),
    cv.test_prob(symp_prob=0.075, start_day='2020-08-01', test_delay=7),

]

pars['interventions'] += [cv.contact_tracing(start_day='2020-03-01',
                               trace_probs={'h': 1, 's': 0.5, 'w': 0.5, 'c': 0.1}, #'c': 0.0
                               trace_time={'h': 1, 's': 3, 'w': 7, 'c': 14}, do_plot=False)]

# Assume B1351 is introduced on Sept 1
day = sim.day('2020-09-01')
b1351 = cv.Strain('b1351', days=day, n_imports=50)
b1351.rel_beta = 1.4
b1351.rel_severe_prob = 1.4
b1351.rel_death_prob = 1.4
b1351.imm_pars['sus'] = dict(form='exp_decay', pars={'init_val': .8, 'half_life': None})
pars['strains'] = [b1351]

# Create sim and run
if __name__ == '__main__':
       
    sim = cv.Sim(pars=pars, datafile='Western_Cape_em.csv')
    if not do_multi: sim.run()

    if do_multi:
        msim = cv.MultiSim(base_sim=sim)
        msim.run(n_runs=4, reseed=True, noise=0)
        msim.reduce()

    # Plotting
    to_plot = sc.objdict({
        'Diagnoses': ['cum_diagnoses'],
        'Daily diagnoses': ['new_diagnoses'],
        'Deaths': ['cum_deaths'],
        'Daily deaths': ['new_deaths'],
        'Total infections': ['cum_infections'],
 #       'Cumulative tests': ['cum_tests'],
 #        'New infections per day': ['new_infections'],
 #        'New Re-infections per day': ['new_reinfections'],
        'New infections by strain': ['new_infections_by_strain']
#        'New tests': ['new_tests'],
    #    'Test yield': ['test_yield'],
    #    'Number quarantined': ['n_quarantined'],
        })


    if do_plot:
        if do_multi:
            msim.plot(to_plot=to_plot, do_save=1, do_show=0, fig_path=f'wcape_calibration.png',
                 legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=35)
        else:
            sim.plot(to_plot=to_plot, fig_args=dict(figsize=(25,20)), do_save=True, do_show=False, fig_path=f'wcape_calibration.png',
                 legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=35)

    if do_save:
        if do_multi: msim.save(f'wcape.msim')
        else:         sim.save(f'wcape.sim')

    # Add histogram
    if plot_hist:

        aggregate = False

        agehists = []
        for s,sim in enumerate(msim.sims):
            agehist = sim['analyzers'][0]
            if s == 0:
                age_data = agehist.data
            agehists.append(agehist.hists[-1])
        raw_x = age_data['age'].values
        raw_deaths = age_data['cum_deaths'].values

        if aggregate:
            x = ["0-29", "30-64", "65-79", "80+"]
            deaths = [raw_deaths[0:6].sum(), raw_deaths[6:13].sum(), raw_deaths[13:16].sum(), raw_deaths[16:].sum()]
        else:
            x = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80+"]
            deaths = raw_deaths

        # From the model
        mdeathlist = []
        for hists in agehists:
            mdeathlist.append(hists['dead'])
        mdeatharr = np.array(mdeathlist)
        low_q = 0.1
        high_q = 0.9
        raw_mdbest = pl.mean(mdeatharr, axis=0)
        raw_mdlow  = pl.quantile(mdeatharr, q=low_q, axis=0)
        raw_mdhigh = pl.quantile(mdeatharr, q=high_q, axis=0)

        if aggregate:
            mdbest = [raw_mdbest[0:6].sum(), raw_mdbest[6:13].sum(), raw_mdbest[13:16].sum(), raw_mdbest[16:].sum()]
            mdlow = [raw_mdlow[0:6].sum(), raw_mdlow[6:13].sum(), raw_mdlow[13:16].sum(), raw_mdlow[16:].sum()]
            mdhigh = [raw_mdhigh[0:6].sum(), raw_mdhigh[6:13].sum(), raw_mdhigh[13:16].sum(), raw_mdhigh[16:].sum()]
        else:
            mdbest = raw_mdbest
            mdlow = raw_mdlow
            mdhigh = raw_mdhigh

        # Plotting
        font_size = 20
        pl.rcParams['font.size'] = font_size
        pl.figure(figsize=(24, 8))
        w = 0.4
        off = .8
        ax = {}
        xl, xr, yb, yt = 0.07, 0.01, 0.07, 0.01
        dx = (1-(xl+xr))
        dy = 1-(yb+yt)
        X = np.arange(len(x))
        XX = X+w-off

        # Deaths
        ax[0] = pl.axes([xl, yb, dx, dy])
        c1 = [0.5, 0.0, 0.0] # deaths
        c2 = [0.9, 0.4, 0.3] # deaths
        pl.bar(X, deaths, width=w, label='Data', facecolor=c1)
        pl.bar(XX, mdbest, width=w, label='Model', facecolor=c2)
        for i,ix in enumerate(XX):
            pl.plot([ix,ix], [mdlow[i], mdhigh[i]], c='k')
        ax[0].set_xticks((X+XX)/2)
        ax[0].set_xticklabels(x)
        pl.xlabel('Age')
        pl.ylabel('Deaths')
        sc.boxoff(ax[0])
        pl.legend(frameon=False, bbox_to_anchor=(0.3,0.7))

        plotname = 'deaths_by_age_agg.png' if aggregate else 'deaths_by_age.png'
        cv.savefig(plotname, dpi=100)
