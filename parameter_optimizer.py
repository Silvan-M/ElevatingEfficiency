from elevator import Elevator
from simulation import Simulation
from building import Building
import distributions
import policies

from concurrent.futures import ThreadPoolExecutor
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from itertools import product
from collections import defaultdict
import random
import csv


current_awt = 9999
current_params = []

num_epochs = 0
learning_rate = 1.03
average_of = 10
simulation_length = 60 * 60 * 6

# Enable gradient descent
gradient_descent = False

# Enable plotting
plot = True
save_plot = "plotter/plots/parameter_optimizer.pdf"

distribution = distributions.HighDensityDistribution() if num_epochs > 0 else None

load_params = "param_optimizer/save_params.txt"
store_params = "param_optimizer/save_params.txt"


def map_parameters(parameters, changed_parameter):
    ret = parameters + [1]
    # ret = [1, parameters[0], 1, parameters[1], parameters[2], parameters[3]]
    if (changed_parameter[0] >= 0):
        ret[changed_parameter[0]] *= changed_parameter[1]
    return ret


def create_simulation(args):
    global current_params
    global distribution

    average_index, parameter_index, parameter_value = args

    policy = policies.PWDPPolicy
    policy_arguments = map_parameters(
        current_params, (parameter_index, parameter_value))

    # Start simulation at a specific time
    hours, minutes, seconds = 0, 0, 0
    elevators = []

    # Standard scenario, set parameters automatically
    floor_amount = distribution.floor_amount
    amount_of_elevators = distribution.amount_of_elevators
    for i in range(amount_of_elevators):
        elevators.append(
            Elevator(
                0,
                floor_amount - 1,
                policy(
                    *policy_arguments),
                distribution.elevator_capacity))

    simulation = Simulation(
        Building(
            elevators=elevators,
            floor_amount=floor_amount,
            distribution=distribution
        )
    )

    simulation.set_time(hours=hours, minutes=minutes, seconds=seconds)
    return simulation


def run_simulation(args):
    (average_index, parameter_index, parameter_value), simulation = args

    simulation.run(seconds=simulation_length, time_scale=-1)
    awt = simulation.statistics.calculate_average_waiting_time()

    return (average_index, parameter_index,
            current_params[parameter_index] * parameter_value), awt


def update_results(results):
    global current_awt
    global current_params

    result_dict = dict(results)

    # Accumulate averages
    accumulated_values = defaultdict(list)
    for (_, parameter_index, parameter_value), awt in result_dict.items():
        accumulated_values[(parameter_index, parameter_value)].append(awt)

    mean_results = {(parameter_index, parameter_value): sum(awts) / len(awts)
                    for (parameter_index, parameter_value), awts in accumulated_values.items()}

    # Choose min AWT of paramter
    min_values = defaultdict(lambda: (float('inf'), None))
    for (parameter_index, parameter_value), awt in mean_results.items():
        current_min_value, _ = min_values[parameter_index]
        if awt < current_min_value:
            min_values[parameter_index] = (awt, parameter_value)

    # Set best parameters
    current_awt = min_values[-1][0]
    for index, (awt, parameter_value) in min_values.items():
        if index >= 0 and awt < current_awt:
            current_params[index] = parameter_value


def write_result(awt, params):
    s = ','.join(map(str, [awt] + params))
    with open(store_params, "a") as file:
        file.write(s + "\n")

if plot or gradient_descent:
    # Load parameters
    with open(load_params, "r") as file:
        lines = file.readlines()
        if lines:
            l = lines[-1].strip().split(',')

            current_awt = float(l[0])
            current_params = [float(value) for value in l[1:]]
        else:
            print("File is empty.")

    min_jump = 1
    max_jump = 1
    for i in range(num_epochs):
        if not gradient_descent:
            continue

        pro = product(
            range(average_of), range(
                len(current_params)), [
                min_jump, max_jump])

        # Run simulations
        simulations = {}
        for a in range(average_of):
            p = (i, -1, 1)
            simulations[p] = create_simulation(p)

        for p in pro:
            simulations[p] = create_simulation(p)

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(run_simulation, simulations.items())

        update_results(results)
        min_jump = random.uniform(1 / learning_rate, 1)
        max_jump = random.uniform(1, learning_rate)

        print(f"Epoch: {i}\tAWT\t{current_awt}\t{current_params}")
        write_result(current_awt, current_params)


    # -----------------------------------------------------------------------------------------------------------
    # Plot parameters and time
    if not plot: 
        exit()

    params_over_time = []
    awt_over_time = []

    with open(store_params, 'r') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            awt_over_time.append(float(row[0]))

            # Extract the rest of the columns
            params_over_time.append(map(float, row[1:]))

    # Transpose the params list for easier plotting
    params_transposed = list(map(list, zip(*params_over_time)))

    # Create a figure and axis for the first y-axis
    fig, ax1 = plt.subplots()

    # Plot parameter values on the first y-axis
    for param_values in params_transposed:
        ax1.plot(param_values, marker='o')

    # Customize the first y-axis
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Parameter Values', color='tab:grey')
    ax1.tick_params('y')
    ax1.legend(['ElevatorButtonWeight',
                'ElevatorButtonTimeWeight',
                'FloorButtonWeight',
                'FloorButtonTimeWeight',
                'CompetitorWeight',
                'DistanceWeight'])
    # ax1.legend(['ElevatorButtonTimeWeight', 'FloorButtonTimeWeight', 'competitor_weight', 'distance_weight'])

    # Create a secondary y-axis
    ax2 = ax1.twinx()

    # Plot scores on the secondary y-axis
    minAWT = min(awt_over_time)
    ax2.plot(awt_over_time, marker='s', alpha=0)
    ax2.set_ylabel('AWT', color='tab:grey')
    ax2.tick_params('y')
    ax2.fill_between(
        np.arange(
            len(awt_over_time)),
        minAWT - 2,
        awt_over_time,
        color='gray',
        alpha=0.3)
    ax2.autoscale(axis='y')

    # Plot a transparent grey area for the scores

    # Customize the plot
    plt.title('Parameter Values Over Epochs')
    fig.set_size_inches(10, 7)
    plt.savefig(save_plot, dpi=300)
    plt.show()