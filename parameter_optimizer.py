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


currentAWT = 9999
currentParams = []

num_epochs = 0
learningRate = 1.05
average_of = 10
simulationLength = 60*60*6

distribution = distributions.HighDensityDistribution() if num_epochs > 0 else None

loadParams = "paramOptimizer/saveParamsBigSmall.txt"
storeParams ="paramOptimizer/saveParamsBigSmall.txt"

def mapParameters(parameters, changedParameter):
    ret = parameters + [1]
    # ret = [1, parameters[0], 1, parameters[1], parameters[2], parameters[3]]
    if(changedParameter[0] >= 0):
        ret[changedParameter[0]] *= changedParameter[1]
    return ret

def createSimulation(args):
    global currentParams
    global distribution

    averageIndex, parameterIndex, parameterValue = args

    policy = policies.PWDPPolicy
    policyArguments = mapParameters(currentParams, (parameterIndex, parameterValue))

    # Start simulation at a specific time
    hours, minutes, seconds = 0, 0, 0
    elevators = [] 

    # Standard scenario, set parameters automatically
    floorAmount = distribution.floorAmount
    amountOfElevators = distribution.amountOfElevators
    for i in range(amountOfElevators):
        elevators.append(Elevator(0, floorAmount-1, policy(*policyArguments), distribution.elevatorCapacity))

    simulation = Simulation(
        Building(
                elevators = elevators,
                floorAmount = floorAmount,
                distribution=distribution
            )
    )

    simulation.setTime(hours=hours, minutes=minutes, seconds=seconds)
    return simulation

def runSimulation(args):
    (averageIndex, parameterIndex, parameterValue), simulation = args

    simulation.run(seconds=simulationLength, timeScale=-1)
    awt = simulation.statistics.calculateAverageWaitingTime()

    return (averageIndex, parameterIndex, currentParams[parameterIndex] * parameterValue), awt

def updateResults(results):
    global currentAWT
    global currentParams

    result_dict = dict(results)

    # Accumulate averages
    accumulated_values = defaultdict(list)
    for (_, parameterIndex, parameterValue), awt in result_dict.items():
        accumulated_values[(parameterIndex, parameterValue)].append(awt)

    mean_results = {
        (parameterIndex, parameterValue): sum(awts) / len(awts) for (parameterIndex, parameterValue), awts in accumulated_values.items()
    }

    # Choose min AWT of paramter
    min_values = defaultdict(lambda: (float('inf'), None))
    for (parameterIndex, parameterValue), awt in mean_results.items():
        current_min_value, _ = min_values[parameterIndex]
        if awt < current_min_value:
            min_values[parameterIndex] = (awt, parameterValue)

    # Set best parameters
    currentAWT = min_values[-1][0]
    for index, (awt, parameterValue) in min_values.items():
        if index >= 0 and awt < currentAWT:
            currentParams[index] = parameterValue

def writeResult(awt, params):
    s = ','.join(map(str, [awt] + params))
    with open(storeParams, "a") as file:
        file.write(s + "\n")

# Load parameters
with open(loadParams, "r") as file:
    lines = file.readlines()
    if lines:
        l = lines[-1].strip().split(',')
        
        currentAWT = float(l[0])
        currentParams = [float(value) for value in l[1:]]
    else:
        print("File is empty.")

minJump = 1
maxJump = 1
for i in range(num_epochs):
    pro = product(range(average_of), range(len(currentParams)), [minJump, maxJump])

    # Run simulations
    simulations = {}
    for a in range(average_of):
        p = (i, -1, 1)
        simulations[p] = createSimulation(p)
        
    for p in pro:
        simulations[p] = createSimulation(p)

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(runSimulation, simulations.items())

    updateResults(results)
    minJump = random.uniform(1/learningRate, 1)
    maxJump = random.uniform(1, learningRate)

    print(f"Epoch: {i}\tAWT\t{currentAWT}\t{currentParams}")
    writeResult(currentAWT, currentParams)


# -----------------------------------------------------------------------------------------------------------
# Plot parameters and time    
paramsOverTime = []
awtOverTime = []

with open(storeParams, 'r') as csvfile:
    reader = csv.reader(csvfile)
    
    for row in reader:
        awtOverTime.append(float(row[0]))
        
        # Extract the rest of the columns
        paramsOverTime.append(map(float, row[1:]))

# Transpose the params list for easier plotting
params_transposed = list(map(list, zip(*paramsOverTime)))

# Create a figure and axis for the first y-axis
fig, ax1 = plt.subplots()

# Plot parameter values on the first y-axis
for param_values in params_transposed:
    ax1.plot(param_values, marker='o')

# Customize the first y-axis
ax1.set_xlabel('Time')
ax1.set_ylabel('Parameter Values', color='tab:blue')
ax1.tick_params('y', colors='tab:blue')
ax1.legend(['ElevatorButtonWeight', 'ElevatorButtonTimeWeight', 'FloorButtonWeight', 'FloorButtonTimeWeight', 'competitorWeight', 'distanceWeight']) 
# ax1.legend(['ElevatorButtonTimeWeight', 'FloorButtonTimeWeight', 'competitorWeight', 'distanceWeight']) 

# Create a secondary y-axis
ax2 = ax1.twinx()

# Plot scores on the secondary y-axis
minAWT = min(awtOverTime)
ax2.plot(awtOverTime, color='tab:grey', marker='s', alpha=0)
ax2.set_ylabel('AWT', color='tab:grey')
ax2.tick_params('y')
ax2.fill_between(np.arange(len(awtOverTime)), minAWT - 2, awtOverTime, color='gray', alpha=0.3)
ax2.autoscale(axis='y')

# Plot a transparent grey area for the scores

# Customize the plot
plt.title('Parameter Values Over Time')
plt.show()