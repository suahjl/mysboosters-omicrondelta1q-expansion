# mysboosters-omicrondelta1q-expansion
This repository contains files required to replicate estimates of **marginal vaccine effectiveness (mVE) against SARS-CoV-2 infection** in "Effectiveness of Homologous and Heterologous AZD1222, CoronaVac, and BNT162b2 Booster Vaccine Against SARS-CoV-2 Infection, and Severe COVID-19: Comparing the Delta- and Omicron-Dominant Periods in Malaysia", presented at the 16th Vaccine Congress 2022, Italy.

The repository contains the following.
1. Python scripts to estimate the mVE against SARS-CoV-2 infection by vaccine combination. These are in the main directory.
2. Anonymised, and cleaned, data vintages consolidated from various **nationally-comprehensive** administrative data sources in Malaysia's national COVID-19 surveillance system, and COVID-19 vaccination drive. These are in the ```Data``` folder.
3. Pre-compiled output files, including additional, more detailed, findings not presented at the congress, e.g., mVE by age groups. These are in the ```Output``` folder.
4. Poster used for the presentation. This can be found in the ```Presentation``` folder.

## Data documentation
### Infection 
The base data set is the Malaysia Vaccine Administration System (MyVAS), which contains COVID-19 vaccination records, and demographics of every person who has received at least one dose of COVID-19 vaccines in Malaysia. These were matched deterministically using national IDs, and passport numbers, with the test data set, which records all supervised COVID-19 tests conducted in Malaysia, both antigen rapid tests (RTK-Ag) and Reverse Transcription Polyamerase Chain Reaction (RT-PCR) tests. Under Malaysian law, the reporting of COVID-19 outcomes are mandatory throughout the study period. These were further matched against data collected in Malaysia's QR code-based automated contact tracing system (AutoTrace), hosted on the national contact tracing application, MySejahtera, to proxy for SARS-CoV-2 exposure risk in the baseline periods (pre-observation); use of MySejahtera is also legally mandated during the study period. 

After applying additional exclusion and inclusion rules, we are left with the following subjects.

- **Delta-dominant analysis**: Adults (aged 18+) who received their primary COVID-19 vaccination between 1 July and 30 September 2021, and either did not take a booster until at least 23 February 2022 or received a booster dose between 27 October 2021 and 4 February 2022. Individuals must have taken a test between 27 October 2021 and 4 February 2022, and never tested positive before 27 February 2022.
- **Omicron-dominant analysis**: Adults (aged 18+) who received their primary COVID-19 vaccination between 1 July and 30 September 2021, and either did not take a booster until at least 23 February 2022 or received a booster dose between 27 October 2021 and 4 February 2022. Individuals must have taken a test between 5 February and 22 February 2022, and never tested positive before 5 February 2022. 

Only individuals who had received AA (2x AZD1222), SS (2x CoronaVac), PP (2x BNT162b2), SSS (3x CoronaVac), SSP (2x CoronaVac + 1x BNT162b2), SSA (2x CoronaVac + 1x AZD1222), PPP (3x BNT162b2), AAP (2x AZD1222 + 1x BNT162b2), or AAA (3x AZD1222) were included.

'id', 'type_comb', 'date1', 'date2', 'date3', 'fullvaxmonth',
       'date_test', 'type', 'result', 'age', 'male', 'trace_count',
       'test_count', 'diabetes', 'hypertension', 'heart', 'asthma', 'cancer',
       'lung', 'kidney', 'liver', 'stroke', 'immunocompromised', 'obese',
       'others', 'n_comorb'

Both data vintages contain the following columns.
1. ```anon_id```: Pseudo-ID (anonymised keys) 
2. ```type_comb```: Type of vaccines received
3. ```date1```: Date of first dose 
4. ```date2```: Date of second dose 
5. ```date3```: Date of third dose 
6. ```fullvaxmonth```: Month of the year 2021 when the individual was deemed fully vaccinated (14-days post-dose 2)
7. ```date_test```: Date of first negative supervised COVID-19 test, or date of first positive supervised COVID-19 test (if ever tested positive)
8. ```type```: Type of COVID-19 test taken
9. ```result```: Result of COVID-19 test taken
10. ```age```: Age
11. ```male```: Sex
12. ```trace_count```: Indicates number of times the individual was identified as a contact of a COVID-19-positive individual (checked into the same place and same time as someone who tests positive by the end of the day) throughout the pre-observation period (before 27 October 2021 for the Delta-dominant analysis, and before 5 February 2022 for the Omicron-dominant analysis)
13. ```test_count```: Indicates number of times the individual had taken supervised COVID-19 tests throughout the pre-observation period (before 27 October 2021 for the Delta-dominant analysis, and before 5 February 2022 for the Omicron-dominant analysis)
14. ```diabetes```: Indicates if the individual self-reported a previous diabetes diagnosis
15. ```hypertension```: Indicates if the individual self-reported an existing hypertension diagnosis
16. ```heart```: Indicates if the individual self-reported an existing cardiovascular disease diagnosis
17. ```asthma```: Indicates if the individual self-reported an existing asthma diagnosis
18. ```cancer```: Indicates if the individual self-reported an existing cancer diagnosis
19. ```lung```: Indicates if the individual self-reported an existing lung disease diagnosis
20. ```kidney```: Indicates if the individual self-reported an existing kidney disease diagnosis
21. ```liver```: Indicates if the individual self-reported an existing liver disease diagnosis
22. ```stroke```: Indicates if the individual self-reported an existing stroke diagnosis
23. ```immunocompromised```: Indicates if the individual self-reported immunocompromised status
24. ```obese```: Indicates if the individual self-reported that they suffer from obesity
25. ```others```: Indicates if the individual self-reported that they suffer from other comorbid conditions
26. ```n_comorb```: The number of self-reported major comorbidities


## Replication guide

1. ```git clone suahjl/mysboosters-omicrondelta1q-expansion```
2. ```pip install requirements.txt```
3. ```delta1q_infection```
4. ```omicron1q_infection```