'''
Simple script for running Covasim scenarios
'''

import pylab as pl
import datetime as dt
import sciris as sc
import covasim as cova
import covid_healthsystems as covidhs


sc.heading('Setting up...')

sc.tic()

# Specify what to run
scenarios = {
    'baseline':     'Status quo',
    'distance':    'Social distancing',
    # 'isolatepos':   'Isolate people who diagnose positive',
}

# Run options
do_run = 1
do_save = 0 # refers to whether to save plot - see also save_sims
do_plot = 1
show_plot = 1
save_sims = 0 # WARNING, huge! (>100 MB)
verbose = 1
n = 3 # Number of parallel runs; change to 3 for quick, 11 for real

# Sim options
interv_day = 10
closure_len = 14
noise = 0.1 # Use noise, optionally
noisepar = 'beta'
seed = 1
reskeys = ['cum_exposed', 'n_exposed']
quantiles = {'low':0.1, 'high':0.9}

# For saving
version  = 'v0'
date     = '2020mar24'
folder   = 'results'
basename = f'{folder}/covasim_scenarios_{date}_{version}'
fig_path   = f'{basename}.png'
obj_path   = f'{basename}.obj'



# If we're rerunning...
if do_run:

    # Order is: results key, scenario, best/low/high
    allres = sc.objdict()
    for reskey in reskeys:
        allres[reskey] = sc.objdict()
        for scenkey in scenarios.keys():
            allres[reskey][scenkey] = sc.objdict()
            for nblh in ['name', 'best', 'low', 'high']:
                allres[reskey][scenkey][nblh] = None # This will get populated below

    for scenkey,scenname in scenarios.items():

        scen_sim = cova.Sim()
        scen_sim.set_seed(seed)

        if scenkey == 'baseline':
            scen_sim['interv_days'] = [] # No interventions
            scen_sim['interv_effs'] = []

        elif scenkey == 'distance':
            scen_sim['interv_days'] = [interv_day] # Close schools for 2 weeks starting Mar. 16, then reopen
            scen_sim['interv_effs'] = [0.7] # Change to 40% and then back to 70%

        elif scenkey == 'isolatepos':
            scen_sim['diag_factor'] = 0.1 # Scale beta by this amount for anyone who's diagnosed

        else:
            raise KeyError


        sc.heading(f'Multirun for {scenkey}')

        scen_sims = cova.multi_run(scen_sim, n=n, noise=noise, noisepar=noisepar, verbose=verbose)

        sc.heading(f'Processing {scenkey}')

        # TODO: this only needs to be done once
        res0 = scen_sims[0].results
        npts = res0[reskeys[0]].npts
        tvec = res0['t']

        scenraw = {}
        for reskey in reskeys:
            scenraw[reskey] = pl.zeros((npts, n))
            for s,sim in enumerate(scen_sims):
                scenraw[reskey][:,s] = sim.results[reskey].values

        scenres = sc.objdict()
        scenres.best = {}
        scenres.low = {}
        scenres.high = {}
        for reskey in reskeys:
            scenres.best[reskey] = pl.mean(scenraw[reskey], axis=1) # Changed from median to mean for smoother plots
            scenres.low[reskey]  = pl.quantile(scenraw[reskey], q=quantiles['low'], axis=1)
            scenres.high[reskey] = pl.quantile(scenraw[reskey], q=quantiles['high'], axis=1)

        for reskey in reskeys:
            allres[reskey][scenkey]['name'] = scenname
            for blh in ['best', 'low', 'high']:
                allres[reskey][scenkey][blh] = scenres[blh][reskey]

        if save_sims:
            print('WARNING: saving sims, which will produce a very large file!')
            allres['sims'] = scen_sims

# Don't run
else:
    allres = sc.loadobj(obj_path)


if do_plot:

    sc.heading('Plotting')

    fig_args = {'figsize': (16, 12)}
    plot_args = {'lw': 3, 'alpha': 0.7}
    scatter_args = {'s': 150, 'marker': 's'}
    axis_args = {'left': 0.10, 'bottom': 0.05, 'right': 0.95, 'top': 0.90, 'wspace': 0.5, 'hspace': 0.25}
    fill_args = {'alpha': 0.2}
    font_size = 18

    fig = pl.figure(**fig_args)
    pl.subplots_adjust(**axis_args)
    pl.rcParams['font.size'] = font_size
    pl.rcParams['font.family'] = 'Proxima Nova' # NB, may not be available on all systems

    # %% Plotting
    for rk, reskey in enumerate(reskeys):
        pl.subplot(len(reskeys), 1, rk + 1)

        resdata = allres[reskey]

        for scenkey, scendata in resdata.items():
            pl.fill_between(tvec, scendata.low, scendata.high, **fill_args)
            pl.plot(tvec, scendata.best, label=scendata.name, **plot_args)

            # interv_col = [0.5, 0.2, 0.4]

            ymax = pl.ylim()[1]

            if reskey == 'cum_exposed':
                sc.setylim()
                pl.title('Cumulative infections')
                pl.text(0.0, 1.1, 'COVID-19 projections, per 1 million susceptibles', fontsize=24,
                        transform=pl.gca().transAxes)

            elif reskey == 'n_exposed':
                pl.legend()
                sc.setylim()
                pl.title('Active infections')

            pl.grid(True)

            # Set x-axis
            xt = pl.gca().get_xticks()
            lab = []
            for t in xt:
                tmp = dt.datetime(2020, 1, 1) + dt.timedelta(days=int(t))  # + pars['day_0']
                lab.append(tmp.strftime('%b-%d'))
            pl.gca().set_xticklabels(lab)
            sc.commaticks(axis='y')

    if do_save:
        pl.savefig(fig_path, dpi=150)
        if do_run:  # Don't resave loaded data
            sc.saveobj(obj_path, allres)

    if show_plot: # Optionally show plot
        pl.show()


#%% Print statistics
for reskey in reskeys:
    for scenkey in list(scenarios.keys()):
        print(f'{reskey} {scenkey}: {allres[reskey][scenkey].best[-1]:0.0f}')


# Perform health systems analysis
hsys = covidhs.HealthSystem(allres)
hsys.analyze()
hsys.plot()

sc.toc()

