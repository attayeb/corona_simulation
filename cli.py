from library2 import *
import json
import click
import gzip


@click.command()
@click.option('--output', prompt="output file name")
@click.option('--simulation_duration', default=50)
@click.option('--msd', default=50)
@click.option('--sv', default='')
@click.option('--relaxation', default = 150)
def main(output, simulation_duration, msd, sv, relaxation):
    first_patient = dict({
        'id': '73a12531-834a-40cc-8729-b168b956b9bb',
        'isinfected': True,
        'parent_infectee': 0,
        'events': {
            'infected': 1,
            'diagnosed': 11,
            'contagious_start': 4,
            'negative': 14,
            'contagious_end': 14
        }
    })

    patients = []
    if sv== '':
        simulation_variables= {
        "transmission_rate": 0.02,
        "exposure_to_infect": [
          1,
          3
        ],
        "diagnosis_to_hospitalization": [
          5,
          10
        ],
        "death_rate": 0.3,
        "quarantation_rate": 80,
        "quarantation_efficacy": 80,
        "hospitalization_rate": 0.2,
        "hospitalization_period_range": [
          7,
          20
        ],
        "duration_of_illness_range": [
          21,
          40
        ],
        "incubation_period_range": [
          3,
          14
        ],
        "contacts_range": [
          10,
          15
        ],
        "reduce_contacts": {
          "day": msd,
          "range": [
            2,
            5
          ]
        },
        "contact_reduction_rate": 0.4,
        "contacts_pool_range": [
          90,
          100
        ],
        "number_of_beds": 200,
        "simulation_population": 1000,
        "simulation_duration": 75
        }
    else:
        with open(sv, 'r') as f:
            simulation_variables = json.load(f)
        
        simulation_variables['contacts_relaxation_day'] = relaxation
        simulation_variables['reduce_contacts']['day'] = msd
        simulation_variables['simulation_duration'] = simulation_duration

    print("Starting simulation")
    sim_res_detailed, sim_res = simulate(simulation_variables)
    print("Simulation finished")
    res = {'simulation_variables': simulation_variables,
           'data_frame': sim_res.to_dict(),
           'detailed_result': sim_res_detailed}
    with gzip.open(output+".gz", "wt", encoding='ascii') as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
