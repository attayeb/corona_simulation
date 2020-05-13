from random import random, sample
from random import choices
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import uuid
from numpy.random import choice
from sklearn.preprocessing import MinMaxScaler

import sys

from pandas import json_normalize

patients = []

first_patient = dict({
    'id': '73a12531-834a-40cc-8729-b168b956b9bb',
    'isinfected': True,
    'events': {
        'infected': 1,
          'diagnosed': 11,
          'contagious_start': 9,
          'negative': 15,
          'contagious_end': 15
    }
})

patients.append(first_patient)

def curveincrease(x):
    tr = np.array([(1.+2/x)**i/x for i in range(0, x)])
    tr = tr.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaler.fit(tr)

    return scaler.fit_transform(tr).flatten()


def curveincreasedecrease(x):
    x1 = curveincrease(int(x/2))
    x2 = np.flip(x1)
    x1 = 0.2 + x1
    return np.concatenate([x1, x2])

def eq(max_x, x):
    return ((-1/max_x) * x) + 1

def decreasing_probability(x):
    return [eq(x-1, i) for i in range(x)]


def infection(pt_assessment, sv):

    global infected
    global pn

    transmission_rate = sv['transmission_rate']
    duration_of_illness = sv['duration_of_illness_range']
    incubation_period = sv['incubation_period_range']
    contacts_range = sv['contacts_range']
    contact_reduction_rate = sv['contact_reduction_rate']
    exposure_to_infect = sv["exposure_to_infect"]
    quarantation_rate = sv['quarantation_rate']
    quarantation_efficacy = sv['quarantation_efficacy']
    simulation_duration = sv['simulation_duration']
    contact_reduction_day = sv['reduce_contacts']['day']
    contact_reduction_range = sv['reduce_contacts']['range']
    try:
        contact_relaxation_day = sv['contacts_relaxation_day']
        relaxation = True
    except:
        relaxation = False
    # if infected >= 12:
    #    return

    #duration = sample(range(duration_of_illness[0], duration_of_illness[1]), 1)[0]
    contagious_start = pt_assessment["events"]["contagious_start"]
    contagious_end = pt_assessment["events"]["contagious_end"]
    diagnosis_day = pt_assessment["events"]['diagnosed']
    infection_day = pt_assessment["events"]['infected']
    patient_id = pt_assessment["id"]
    # print(parent_infectee)
    if infection_day > simulation_duration:
        return

    pool = 500
    total_contacts = 0
    reduction_probability = decreasing_probability((contagious_end - contagious_start) + 30)
    for day in range(contagious_start, contagious_end+1):

        number_of_contacts = sample(
            range(contacts_range[0], contacts_range[1]), 1)[0]

        if relaxation:
            if (contact_reduction_day <= day < contact_relaxation_day):
                number_of_contacts = sample(
                    range(contact_reduction_range[0], contact_reduction_range[1]), 1)[0]
        else:
            if (day >= contact_reduction_day):
                number_of_contacts = sample(
                    range(contact_reduction_range[0], contact_reduction_range[1]), 1)[0]
        if day >= diagnosis_day:
            #print("contacts before quarantine", number_of_contacts)
            number_of_contacts = int(
                number_of_contacts * (1-(quarantation_rate * quarantation_efficacy)))
            #print("contacts after quarantine", number_of_contacts)

        total_contacts = total_contacts + number_of_contacts

        if (number_of_contacts > 0) and (total_contacts < pool):

            for i in range(number_of_contacts):
                contact_day = day
                rnd = random()

                tr = transmission_rate
                tr = tr * reduction_probability[day - contagious_start]
                #tr = tr * (1-(number_of_infectee/total_contacts))
                #print(contact_day, tr)
                transmission = choices([True, False], weights=[tr, 1-tr])[0]
                if transmission:
                    ret = assess_patient(
                        day, patient_id, isinfected=True, sv=sv)
                    patients.append(ret)

                    infection(ret, sv)

    return


def assess_patient(infection_day, parent_id, sv, isinfected=True):
    hospitalization_period_range = sv['hospitalization_period_range']
    duration_of_illness_range = sv['duration_of_illness_range']
    incubation_period_range = sv['incubation_period_range']
    death_rate = sv['death_rate']
    hospitalization_rate = sv['hospitalization_rate']
    exposure_to_infcet = sv['exposure_to_infect']
    diagnosis_to_hospitaliztion = sv['diagnosis_to_hospitalization']
    asymptomatic_transmission_range = sv['asymptomatic_transmission_range']

    events = {}
    patient = {}
    patient['id'] = str(uuid.uuid4())
    patient['parent_id'] = parent_id

    if isinfected:
        incubation_period = sample(range(incubation_period_range[0], incubation_period_range[1]), 1)[0]
        duration_of_illness = sample(range(duration_of_illness_range[0], duration_of_illness_range[1]), 1)[0]
        patient["isinfected"] = True
        patient["incubation_period"] = incubation_period
        patient["duration_of_illness"] = duration_of_illness
        events['infected'] = infection_day
        diagnosis_day = infection_day + incubation_period + sample(range(duration_of_illness), 1)[0]
        events["diagnosed"] = diagnosis_day
        asymptomatic_transmission = sample(range(asymptomatic_transmission_range[0], asymptomatic_transmission_range[1]), 1)[0]
        events["contagious_start"] = infection_day + incubation_period - asymptomatic_transmission

        hospitalization = choices([True, False], weights=[
                                  hospitalization_rate, 1-hospitalization_rate])[0]
        # hospits.append(hospitalization)
        # print(hospitalization)
        if hospitalization:
            hospitalization_day = diagnosis_day + sample(range(diagnosis_to_hospitaliztion[0],
                                                               diagnosis_to_hospitaliztion[1]), 1)[0]
            events['hospitalized'] = hospitalization_day
            events['symptoms_start'] = infection_day + incubation_period
            events["contagious_end"] = hospitalization_day
            if random() < death_rate:
                # print("dead")
                death_day = hospitalization_day + sample(range(hospitalization_period_range[0],
                                                               hospitalization_period_range[1]), 1)[0]
                events['death'] = death_day
            else:
                # print("discharge")
                discharge_day = hospitalization_day + sample(range(hospitalization_period_range[0],
                                                                   hospitalization_period_range[1]), 1)[0]
                events['discharge'] = discharge_day

        else:
            # negative_day > diagnosis_day < duration_of_illness
            negative_day = sample(range(diagnosis_day, infection_day + incubation_period + duration_of_illness_range[1]), 1)[0]
            #negative_day = diagnosis_day + \
            #    sample(range(duration_of_illness_range[0], duration_of_illness_range[1]), 1)[0]
            events['negative'] = negative_day
            events["contagious_end"] = negative_day
    else:
        patient["isinfected"] = False

    # print(events)
    patient['events'] = events

    return patient


def get_results(patients):
    ndf = json_normalize(patients)
    # print(ndf.columns)
    ndf = ndf.drop('isinfected', axis=1)
    ndf = ndf.melt(id_vars=['parent_id', 'id']).dropna(
    ).sort_values('value').reset_index()

    acu_infected = 0
    infected = 0
    cured = 0
    dead = 0
    hospitalized = 0
    active = 0
    diagnosed = 0
    res = []

    for row in ndf.iterrows():

        if row[1]['variable'] == 'events.infected':
            acu_infected = acu_infected + 1
            infected = infected + 1

        if row[1]['variable'] == 'events.negative':
            cured = cured + 1
            active = active - 1
            infected = infected - 1

        if row[1]['variable'] == 'events.cured':
            cured = cured + 1
            active = active - 1
            infected = infected - 1

        if row[1]['variable'] == 'events.hospitalized':
            hospitalized = hospitalized + 1

        if row[1]['variable'] == 'events.discharge':
            hospitalized = hospitalized - 1
            active = active - 1
            cured = cured + 1
            infected = infected - 1

        if row[1]["variable"] == "events.diagnosed":
            diagnosed = diagnosed + 1
            active = active + 1

        if row[1]['variable'] == 'events.death':
            dead = dead + 1
            active = active - 1
            hospitalized = hospitalized - 1
            infected = infected - 1

        res.append({'day': row[1]['value'],
                    'acu_infected': acu_infected,
                    'active': active,
                    'infected': infected,
                    'cured': cured,
                    'dead': dead,
                    'hospitalized': hospitalized,
                    'diagnosed': diagnosed})

    return res


def plot(mdf, maxy=10000, maxx=100):
    plt.figure(figsize=(25, 10))
    plt.bar(mdf["day"], mdf['active'], label="active", alpha=0.5)
    plt.bar(mdf["day"], mdf['hospitalized'], label="hospitalized", alpha=0.5)
    plt.bar(x=mdf["day"], height=mdf['dead'],
            label="accumulated death", alpha=0.5)
    plt.hlines(simulation_variables['number_of_beds'], 0,
               simulation_variables['simulation_duration'], linestyles='dotted', label="Hospital capacity")
    plt.xlim([0, maxx])
    plt.ylim([0, maxy])
    plt.legend()
    plt.show()


def simulate(simulation_variables, toplot=False):
    global patients
    infected = 0
    pn = simulation_variables['simulation_population']
    result = infection(first_patient, sv=simulation_variables)
    print("simulation finished")
    mdf = pd.DataFrame(get_results(patients))
    mdf = pd.DataFrame(mdf.groupby('day').tail(1)).reset_index()
    mdf.drop('index', axis='columns', inplace=True)
    if toplot:
        plot(mdf)
    return patients, mdf


if __name__ == "__main__":
    pass
