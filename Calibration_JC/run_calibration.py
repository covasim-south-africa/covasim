import os
import shutil as sh
import sciris as sc
import optuna as op
import create_sim as cs


def get_fn():
    ''' Get a filename from the date '''
    string = sc.sanitizefilename(str(sc.now())).replace(' ', '_')
    return string


def objective(trial):
    ''' Define the objective for Optuna '''
    pars = {}
    bounds = cs.define_pars(which='bounds')
    for key, bound in bounds.items():
        pars[key] = trial.suggest_uniform(key, *bound)
    pars['rand_seed'] = trial.number
    mismatch = cs.run_sim(pars)
    try:
        pars['mismatch'] = mismatch
        sc.savejson(f'./progress/trial{trial.number}_{get_fn()}.pars', pars)
    except Exception as E:
        print(f'Could not save progress file; {str(E)}')
    return mismatch


def worker():
    ''' Run a single worker '''
    try:
        study = op.load_study(storage=storage, study_name=name)
        output = study.optimize(objective, n_trials=n_trials)
    except Exception as E:
        print(f'An exception was encountered! {E}')
        string = '\n\n'.join([storage, str(E), sc.traceback()])
        fn = f'optuna_exception_{get_fn()}.err'
        sc.savetext(fn, string)
        output = str(E)
    return output


def run_workers():
    ''' Run multiple workers in parallel '''
    output = sc.parallelize(worker, n_workers)
    return output


def make_study(restart=False):
    ''' Make a study, deleting one if it already exists '''
    try:
        if restart:
            print(f'About to delete {storage}:{name}, you have 5 seconds to intervene!')
            sc.timedsleep(5.0)
            op.delete_study(storage=storage, study_name=name)
    except:
        pass
    output = op.create_study(storage=storage, study_name=name, load_if_exists=not (restart))
    return output


if __name__ == '__main__':

    restart = 0
    do_plot = 0
    local = 1  # Set whether to run locally -- just for testing

    n_opt = [10, 2][local]
    n_trials = [150, 3][local]
    n_workers = [36, 4][local]

    try:
        sh.rmtree('./progress/', ignore_errors=True)
        os.makedirs('./progress/', exist_ok=True)
    except Exception as E:
        print(f'Could not make progress folder: {E}')


    for opt in range(n_opt):
        name = f'RSA_calib_round1'
        storage = f'sqlite:///opt_rnr_batch46_sg_v{opt}.db'

        t0 = sc.tic()
        make_study(restart=restart)
        run_workers()
        study = op.load_study(storage=storage, study_name=name)
        best_pars = study.best_params
        T = sc.toc(t0, output=True)
        print(f'Output: {best_pars}, time: {T}')

        if local and do_plot:
            cs.run_sim(best_pars, interactive=True)