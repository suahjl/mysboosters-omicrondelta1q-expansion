# Codes for tabulating the prevalence of self-reported major comorbidities in the population of Malaysia
# The source files contain sensitive PIIs, and cannot be shared at present
# These codes are released for transparency regardless

import pandas as pd
import numpy as np
import time
import telegram_send
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

time_start = time.time()

# 0 --- Preliminaries
file_vax = 'Data/vax_linelist.parquet'  # The source file contains sensitive PIIs, and cannot be shared at present
file_comorb = 'Data/vaxreg_comorb.parquet'  # The source file contains PIIs sensitive, and cannot be shared at present
# Setup
list_vax = ['ss', 'pp', 'aa', 'ppp', 'aap', 'aaa','ssp', 'ssa', 'sss']
list_baseX = ['agegroup', 'state', 'ethnicity', 'nationality', 'male', 'frontliner', 'private2']
list_comorbX = ['diabetes', 'hypertension', 'heart', 'asthma',
                'cancer', 'lung', 'kidney', 'liver', 'stroke',
                'immunocompromised', 'obese', 'others']
list_ncomorbX = ['n_comorb']
list_X = list_baseX + list_comorbX + list_ncomorbX

# I --- Read Data frames
print('\n----- Reading Base Vax -----')
time_start_interim = time.time()
df = pd.read_parquet(file_vax)
print('\n----- Input file read in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

print('\n----- Reading Comorb -----')
time_start_interim = time.time()
df_comorb = pd.read_parquet(file_comorb)
print('\n----- Input file read in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# II.A --- Wrangle base vax
print('\n----- Wrangle base vax -----')
time_start_interim = time.time()
print('Age restriction')
df = df[df['age'] >= 18]
print('Type comb')
df['type_comb'] = df['brand1'] + df['brand2'] + df['brand3']
df.loc[df['type_comb'].isna(), 'type_comb'] = df['brand1'] + df['brand2']
df.loc[df['type_comb'].isna(), 'type_comb'] = df['brand1']
df.loc[df['type_comb'].isna(), 'type_comb'] = '0'
df = df[df['type_comb'].isin(list_vax)]  # restrict types considered
print('Age group')
df.loc[(df['age'] < 18), 'agegroup'] = '0-17'
df.loc[((df['age'] >= 18) & (df['age'] < 30)), 'agegroup'] = '18-29'
df.loc[((df['age'] >= 30) & (df['age'] < 40)), 'agegroup'] = '30-39'
df.loc[((df['age'] >= 40) & (df['age'] < 50)), 'agegroup'] = '40-49'
df.loc[((df['age'] >= 50) & (df['age'] < 60)), 'agegroup'] = '50-59'
df.loc[((df['age'] >= 60) & (df['age'] < 70)), 'agegroup'] = '60-69'
df.loc[((df['age'] >= 70) & (df['age'] < 80)), 'agegroup'] = '70-79'
df.loc[(df['age'] >= 80), 'agegroup'] = '80+'
list_agegroup = ['0-17', '18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
print('Nationality')
df.loc[~(df['nationality'] == 'MYS'), 'nationality'] = 0  # non-Malaysians or missing
df.loc[(df['nationality'] == 'MYS'), 'nationality'] = 1  # non-Malaysians or missing
print('Redundant columns')
del df['age']
del df['brand1']
del df['brand2']
del df['brand3']
print('\n----- Base vax wrangled in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# II.B --- Wrangle comorb
print('\n----- Wrangle comorb -----')
time_start_interim = time.time()
print('\n----- Comorb wrangled in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# III --- Merge
print('\n----- Merging -----')
time_start_interim = time.time()
print('Base Vax <<--- Comorb')
df = df.merge(df_comorb, on='id', how='left')
print('\n----- Merged in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# IV --- Functions
print('\n----- Defining functions -----')
time_start_interim = time.time()


def tabstat(data=df, vertical='', horizontal=''):
    tab = pd.crosstab(data[horizontal], data[vertical])
    perc = pd.crosstab(data[horizontal], data[vertical], normalize='index') # by row
    perc = 100 * perc # in % terms
    perc = perc.round(1) # 1 decimal point
    return tab, perc


def heatmap(input=pd.DataFrame(), colourmap='magma_r', outputpath='', titletext='', title=True):
    fig = plt.figure()
    d = input.copy()
    labels = input.copy()
    d = np.log(d)
    d = d.replace(np.inf, np.nan)  # log(0)
    d = d.replace(-np.inf, np.nan)  # log(0)
    sns.heatmap(d, annot=labels, cmap=colourmap, center=0, annot_kws={'size':12}, cbar=False)
    if title == True:
        plt.title(titletext)
    elif title == False:
        pass
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    fig.tight_layout()
    fig.savefig(outputpath)
    return fig


print('\n----- Functions defined in ' + "{:.0f}".format(time.time() - time_start_interim) + ' seconds -----')

# V --- Tabulate
# By vax type
k = 1
for i in tqdm(list_comorbX):
    tab, perc = tabstat(data=df, vertical=i, horizontal='type_comb')
    tab = tab.rename(columns={1:i})
    perc = perc.rename(columns={1: i})
    tab = tab[i]
    perc = perc[i]
    if k == 1:
        tab_vax = tab.copy()
        perc_vax = perc.copy()
    elif k > 1:
        tab_vax = pd.concat([tab_vax, tab], axis=1)
        perc_vax = pd.concat([perc_vax, perc], axis=1)
    k += 1
fig = heatmap(perc_vax,
              outputpath='Output/MYSBoosters_ComorbBreakdown_Perc_Vax.png',
              titletext='Prevalence of Major Comorbidities by Vaccination Group (%)')
## By age
k = 1
for i in tqdm(list_comorbX):
    tab, perc = tabstat(data=df, vertical=i, horizontal='agegroup')
    tab = tab.rename(columns={1:i})
    perc = perc.rename(columns={1: i})
    tab = tab[i]
    perc = perc[i]
    if k == 1:
        tab_vax = tab.copy()
        perc_vax = perc.copy()
    elif k > 1:
        tab_vax = pd.concat([tab_vax, tab], axis=1)
        perc_vax = pd.concat([perc_vax, perc], axis=1)
    k += 1
fig = heatmap(perc_vax,
              outputpath='Output/MYSBoosters_ComorbBreakdown_Perc_Age.png',
              titletext='Prevalence of Major Comorbidities by Age Group (%)')

### End
print('\n----- Ran in ' + "{:.0f}".format(time.time() - time_start) + ' seconds -----')