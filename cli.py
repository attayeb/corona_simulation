from simulation import *
import json
import click
import gzip


@click.command()
@click.option('--output', prompt="output file name")
@click.option('--simulation_variables_file', prompt="simulation variables file")
@click.option('--simulation_duration', default=50)
@click.option('--contact_reduction_day', default=50)
@click.option('--relaxation', default = 150)

def main(output, simulation_variables_file, simulation_duration, contact_reduction_day, relaxation):
    patients = []
    with open(simulation_variables_file, 'r') as f:
        simulation_variables = json.load(f)
        
    simulation_variables['contacts_relaxation_day'] = relaxation
    simulation_variables['reduce_contacts']['day'] = contact_reduction_day
    simulation_variables['simulation_duration'] = simulation_duration

    print("Simulation started")
    sim_res_detailed, sim_res = simulate(simulation_variables)
    print("Simulation finished")
    res = {'simulation_variables': simulation_variables,
           'data_frame': sim_res.to_dict(),
           'detailed_result': sim_res_detailed}
    with gzip.open(output+".gz", "wt", encoding='ascii') as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
