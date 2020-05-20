from random import random, sample
from random import choices

import pandas as pd
import uuid

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


def eq(max_x, x):
    """Returns equally separated decreasing float values from 1 to 0 depending on the maximu value of x

    Parameters
    ----------
    max_x : int
        maximum x value (maximum number of steps)
    x : int
        current x value (step)

    Returns
    -------
    float
        y value

    Example
    -------
    >>> eq(3, 0)
    1.0
    >>> eq(3, 1)
    0.6666666666666667
    >>> eq(3, 3)
    0.0
    """
    return ((-1/max_x) * x) + 1

def decreasing_probability(x):
    return [eq(x-1, i) for i in range(x)]


def infection(pt_assessment, sv):
    """The main simulation function

    Parameters
    ----------
    pt_assessment : dict
        Patient attributes
    sv : dict
        simultaion variables
    """
      
    global infected

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
    
    contagious_start = pt_assessment["events"]["contagious_start"]
    contagious_end = pt_assessment["events"]["contagious_end"]
    diagnosis_day = pt_assessment["events"]['diagnosed']
    infection_day = pt_assessment["events"]['infected']
    patient_id = pt_assessment["id"]

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
            number_of_contacts = int(
                number_of_contacts * (1-(quarantation_rate * quarantation_efficacy)))

        total_contacts = total_contacts + number_of_contacts

        if (number_of_contacts > 0) and (total_contacts < pool):

            for i in range(number_of_contacts):
                contact_day = day
                rnd = random()

                tr = transmission_rate
                tr = tr * reduction_probability[day - contagious_start]
                transmission = choices([True, False], weights=[tr, 1-tr])[0]
                if transmission:
                    ret = assess_patient(
                        day, patient_id, isinfected=True, sv=sv)
                    patients.append(ret)

                    infection(ret, sv)

    return


def assess_patient(infection_day, parent_id, sv, isinfected=True):
    """Gives patient characteristics randomly depending on simulation_variable input

    Parameters
    ----------
    infection_day : int
        contact day = the day getting infected
    parent_id : str
        the id of the case who transmitted the infection
    sv : dict
        simulation_variable dictionary
    isinfected : bool, optional
        Determines if the case is infected after contact, by default True

    Returns
    -------
    dict
        The details of the case attributes.
    """
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

        if hospitalization:
            hospitalization_day = diagnosis_day + sample(range(diagnosis_to_hospitaliztion[0],
                                                               diagnosis_to_hospitaliztion[1]), 1)[0]
            events['hospitalized'] = hospitalization_day
            events['symptoms_start'] = infection_day + incubation_period
            events["contagious_end"] = hospitalization_day
            if random() < death_rate:
                death_day = hospitalization_day + sample(range(hospitalization_period_range[0],
                                                               hospitalization_period_range[1]), 1)[0]
                events['death'] = death_day
            else:
                discharge_day = hospitalization_day + sample(range(hospitalization_period_range[0],
                                                                   hospitalization_period_range[1]), 1)[0]
                events['discharge'] = discharge_day

        else:
            
            negative_day = sample(range(diagnosis_day, infection_day + incubation_period + duration_of_illness_range[1]), 1)[0]
            events['negative'] = negative_day
            events["contagious_end"] = negative_day
    else:
        patient["isinfected"] = False

    # print(events)
    patient['events'] = events

    return patient


def get_results(patients):
    """Summarizes the simulated results

    Parameters
    ----------
    patients : list of dictionaries
        The attributes of the simulated cases 

    Returns
    -------
    list
        Daily statistics of simultion results.
    """
    

    ndf = json_normalize(patients)
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


def simulate(simulation_variables):
    """Simulation running (main function)

    Parameters
    ----------
    simulation_variables : dict
        The details of the simulation parameters.

    Returns
    -------
    list, pandas.DataFrame
        list: The cases list of dictionaries, containing the details of the simulation result.
        pandas.DataFrame: Daily statistics of simulation.
    """
    global patients
    infected = 0
    result = infection(first_patient, sv=simulation_variables)
    print("simulation finished")
    mdf = pd.DataFrame(get_results(patients))
    mdf = pd.DataFrame(mdf.groupby('day').tail(1)).reset_index()
    mdf.drop('index', axis='columns', inplace=True)
    return patients, mdf


if __name__ == "__main__":
    pass
