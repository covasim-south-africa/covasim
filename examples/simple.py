'''
Simplest possible Covasim usage example.
'''

import covasim as cv

folder   = 'data'
basename = f'{folder}/SA_observed_data_Fin'
file_path = f'{basename}.xlsx'


sim = cv.Sim(datafile = file_path, datacols = ['t', 'cum_recoveries', 'cum_infections', 'new_infections', 'cum_deaths', 'n_infectious', 'new_recoveries', 'new_deaths', 'date'])
sim.run()
sim.plot()