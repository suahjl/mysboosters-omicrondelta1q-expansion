# Replication codes for the infection analysis (Delta-predominance)

import pandas as pd
import numpy as np
import time
import telegram_send
import dataframe_image as dfi
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

import statsmodels.formula.api as smf

time_start = time.time()

# 0 --- Preliminaries
file_input = 'Data/MYSBoosters_TND_Data_Omicron1Q_Expansion.parquet'  # Omicron1Q_Expansion DATA

# I --- Data
print('\n----- Reading processed data file -----')
time_start_interim = time.time()
df = pd.read_parquet(file_input)
for i in ['date1', 'date2', 'date3', 'date_test']:
    df.loc[df[i] == '0', i] = np.nan  # supposedly missing
    df[i] = pd.to_datetime(df[i]).dt.date
print('\n----- Input file read in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# II --- Further cleaning (specific to analysis)
print('\n----- Further cleaning -----')
time_start_interim = time.time()
# Redefine: reference group
df.loc[df['type_comb'] == 'pp', 'type_comb'] = '0_pp'
print('\n----- Further cleaning completed in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# III --- Set up Logit
print('\n----- Setting up model -----')
time_start_interim = time.time()
# Controls
list_X = ['age', 'male', 'trace_count', 'test_count', 'C(fullvaxmonth)',
          'diabetes', 'hypertension', 'heart', 'asthma', 'cancer',
          'lung', 'kidney', 'liver', 'stroke', 'immunocompromised', 'obese',
          'others']
controls_X = '+'.join(list_X)
# Treatment
treatment_D = 'C(type_comb)'
# Equation
eqn = 'result' + '~' + treatment_D + '+' + controls_X
# Optimisation method
opt_method = 'ncg'
opt_maxiter = 250  # maximum iterations
# Number of vax combos considered
n_treatment_D = len(list(df['type_comb'].unique()))  # first one is omitted
print('\n----- Model set up in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# IV --- Estimation function
print('\n----- Defining functions -----')
time_start_interim = time.time()
def logitVE(equation=eqn,
            method=opt_method,
            maxiter=opt_maxiter,
            data=df,
            n_keep=n_treatment_D,
            output_suffix=''):
    _mod = smf.logit(equation, data=data)
    _result = _mod.fit(method=method, maxiter=maxiter)
    print(_result.summary())
    _VE = 100 * (1 - np.exp(_result.params))
    _VE = _VE.iloc[1:n_keep]
    _CI = 100 * (1 - np.exp(_result.conf_int()))
    _CI = _CI.iloc[1:n_keep, :]
    _CI.rename(columns={0: 'UB', 1: 'LB'}, inplace=True)
    _CI = _CI[['LB', 'UB']]
    _VE = pd.concat([_VE, _CI], axis=1)
    _VE.rename(columns={0:'mVE'}, inplace=True)
    _VE = _VE.round(2)
    _VE.index = _VE.index.str.replace('C(type_comb)[T.', '', regex=False)
    _VE.index = _VE.index.str.replace(']', '', regex=False)

    fig = plt.figure()
    labels = _VE.copy()
    # d = np.log(_VE)
    # d = d.replace(np.inf, np.nan)  # log(0)
    # d = d.replace(-np.inf, np.nan)  # log(0)
    sns.heatmap(_VE, annot=labels, cmap='magma', center=0, annot_kws={'size': 20}, fmt='g', cbar=False)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    fig.tight_layout()
    fig.savefig('Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_VE_' + output_suffix + '_Heatmap.png')

    _comorb_AOR = np.exp(_result.params)
    _comorb_AOR = _comorb_AOR.iloc[n_keep:]
    _comorb_AOR_CI = 1 - np.exp(_result.conf_int())
    _comorb_AOR_CI = _comorb_AOR_CI.iloc[n_keep:, :]
    _comorb_AOR_CI.rename(columns={0: 'LB', 1: 'UB'}, inplace=True)
    _comorb_AOR = pd.concat([_comorb_AOR, _comorb_AOR_CI], axis=1)
    _comorb_AOR.rename(columns={0: 'AOR'}, inplace=True)
    _comorb_AOR = _comorb_AOR.round(2)

    dfi.export(_VE, 'Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_VE_' + output_suffix + '.png')
    _VE.to_csv('Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_VE_' + output_suffix + '.csv')

    dfi.export(_comorb_AOR, 'Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_comorbAOR_' + output_suffix + '.png')
    _comorb_AOR.to_csv('Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_comorbAOR_' + output_suffix + '.csv')

    return _VE, _comorb_AOR, _result, _mod

print('\n----- Functions defined in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# V --- Estimation
print('\n----- Estimating models -----')
time_start_interim = time.time()
# Consolidated
VE_consol = pd.DataFrame(columns=['agegroup', 'mVE', 'LB', 'UB'])
# Infection
VE, comorb_AOR, result, mod = logitVE(output_suffix='Full')
VE['agegroup'] = 0
VE_consol = pd.concat([VE_consol, VE], axis=0)
# Infection: age-strat
df.loc[(df['age'] >= 18) & (df['age'] < 40), 'agegroup'] = 1
df.loc[(df['age'] >= 40) & (df['age'] < 60), 'agegroup'] = 2
df.loc[(df['age'] >= 60), 'agegroup'] = 3
for k, suffix in tqdm(zip(range(1, df['agegroup'].max().astype('int') + 1), ['Age1', 'Age2', 'Age3'])):
    d = df[df['agegroup'] == k]  # subset
    telegram_send.send(conf='EcMetrics_Config_GeneralFlow.conf',
                       messages=['Age Group: ' + str(k)])
    VE_strat, comorb_AOR_strat, result_strat, mod_strat = logitVE(data=d, output_suffix=suffix)
    VE_strat['agegroup'] = k
    VE_consol = pd.concat([VE_consol, VE_strat], axis=0)
VE_consol.to_csv('Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_VE_consol.csv', index=True)
dfi.export(VE_consol, 'Output/MYSBoosters_TND_Est1a_Omicron1Q_Expansion_VE_consol.png')
print('\n----- Models estimated in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# End
print('\n----- Ran in ' + "{:.0f}".format(time.time() - time_start) + ' seconds -----')
