import numpy as np

import malaria_skeleton as malaria
import malaria_visualize


# dictionairy where values are list of type:
# value, changable (True/False), minimum, maximum
# where the last two are only present when parameter is changable
parameters = {
    "width": [50, False],
    "height": [50, False],
    "nHuman": [100, True, 1, 100],
    "nMosquito": [200, True, 1, 500],
    "initMosquitoHungry": [0.9, True, 0.0, 1.0],
    "initMosquitoInfected": [0.0, True, 0.0, 1.0],
    "initHumanInfected": [0.9, True, 0.0, 1.0],
    "humanInfectionProb": [0.8, True],
    "mosquitoInfectionProb": [0.8, True, 0.0, 1.0],
    "humanDeathByInfectionProb": [0.5, True, 0.0, 1.0],
    "biteProb": [0.9, True, 0.0, 1.0],
    "mealInterval": [3, True, 1, 100],
    "infectionPeriod": [20, True, 1, 100],
    "immuntiyPeriod": [4, True, 1, 100],
}

# 50, 50, 100, 200, 0.9, 0.0, 1.0, 0.8, 0.8, 0.5, 0.9, 3, 20, 4

parameter_values = [parameters.get(key)[0] for key in parameters.keys()]
parameter_changable = [parameters.get(key)[1] for key in parameters.keys()]
indeces = np.where(parameter_changable)[0]
parameter_step_keys = np.array(list(parameters.keys()))[indeces]


sim = malaria.Model(*parameter_values)
vis = malaria_visualize.Visualization(sim.height, sim.width)

# indicate which attributes to store measurements from
attributes = {
    "death_counts": sim.deathCount,
    "infected_counts": sim.infectedCount,
}  ### NOT what I want, value in dictionary, not the method...

# store measurements in dictionairy
measurements = dict.fromkeys(attributes.keys(), [])

for t in range(1000):
    for sim_attribute in attributes.keys():
        sim.update()
        if t % 100 == 0:
            vis.update(t, sim.mosquitoPopulation, sim.humanPopulation)

        measurements[sim_attribute].append(attributes[sim_attribute])
vis.persist()

print(measurements["death_counts"][-10:])
