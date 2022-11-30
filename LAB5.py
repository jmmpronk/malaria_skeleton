import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import malaria_skeleton as malaria
import malaria_visualize
from malaria_skeleton import Model


# dictionairy where values are list of type:
# value, changable (True/False), minimum, maximum
# where the last two are only present when parameter is changable
parameters = {
    "width": [50, False],
    "height": [50, False],
    "nHuman": [200, True, 1, 100],
    "nMosquito": [500, True, 1, 500],
    "initMosquitoHungry": [0.9, True, 0.0, 1.0],
    "initMosquitoInfected": [0.0, True, 0.0, 1.0],
    "initHumanInfected": [0.2, True, 0.0, 1.0],
    "humanInfectionProb": [0.5, True],
    "mosquitoInfectionProb": [0.5, True, 0.0, 1.0],
    "humanDeathByInfectionProb": [0.004, True, 0.0, 1.0],
    "biteProb": [0.9, True, 0.0, 1.0],
    "mealInterval": [3, True, 1, 100],
    "infectionPeriod": [20, True, 1, 100],
    "immuntiyPeriod": [20, True, 1, 100],
    "humanNaturalDeathProb": [0.001, False],
    "mosquitoNaturalDeathProb": [0.01, False],
}

# width=50,
# height=50,
# nHuman=200,
# nMosquito=500,
# initMosquitoHungry=0.9,
# initMosquitoInfected=0,
# initHumanInfected=0.2,
# humanInfectionProb=0.5,
# mosquitoInfectionProb=0.5,
# humanDeathByInfectionProb=0.004,
# biteProb=0.9,
# mealInterval=3,
# infectionPeriod=20,
# immuntiyPeriod=20,
# humanNaturalDeathProb=0.001,
# mosquitoNaturalDeathProb=0.01,

# parameter_values = [parameters.get(key)[0] for key in parameters.keys()]
# parameter_changable = [parameters.get(key)[1] for key in parameters.keys()]
# indeces = np.where(parameter_changable)[0]
# parameter_step_keys = [list(parameters.keys())[i] for i in indeces]
# print(parameter_step_keys)


def parameter_sweep(steps, init_parameters, parameter, values):

    # create dictionairy of dataframes, one for each parameter value
    data_dict = dict()

    for value in values:

        # initialize dataframe
        df = pd.DataFrame([], columns=["t", "infection_fraction"])

        # get list of parameters
        parameters = init_parameters

        # update value of sweeped parameter
        old = parameters[parameter]
        new = old
        new[0] = value

        # make list of parameter values
        parameter_values = [parameters.get(key)[0] for key in parameters.keys()]

        # initialize model
        sim = Model(*parameter_values)

        # initialize list of infection_fractions and of corresponding times
        infection_fractions = []
        t_list = []

        # simulate
        for t in range(steps):

            if t % int(steps / 10) == 0:
                print(f"value = {value}, t = {t}")

            data = sim.update()

            # save data for last 20% of time steps
            if t >= 0.8 * steps:
                t_list.append(t)
                infection_fractions.append(data[0])

        df["t"] = t_list
        df["infection_fraction"] = infection_fractions

        data_dict[str(value)] = df

    return data_dict


data = parameter_sweep(
    steps=2000,
    init_parameters=parameters,
    parameter="nHuman",
    values=[50, 100, 300, 500],
)

for i, key in enumerate(data.keys()):
    df = data[key]
    plt.plot(df["t"], df["infection_fraction"], label="nHuman = " + key)

plt.xlabel("t")
plt.ylabel("infection fraction")
plt.legend()
plt.savefig("nHumans_vs_infection.png")
plt.show()


# sim = malaria.Model(*parameter_values)
# vis = malaria_visualize.Visualization(sim.height, sim.width)

# # indicate which attributes to store measurements from
# attributes = {
#     "death_counts": sim.deathCount,
#     "infected_counts": sim.infectedCount,
# }  ### NOT what I want, value in dictionary, not the method...

# # store measurements in dictionairy
# measurements = dict.fromkeys(attributes.keys(), [])

# for t in range(1000):
#     for sim_attribute in attributes.keys():
#         sim.update()
#         if t % 100 == 0:
#             vis.update(t, sim.mosquitoPopulation, sim.humanPopulation)

#         measurements[sim_attribute].append(attributes[sim_attribute])
# vis.persist()

# print(measurements["death_counts"][-10:])
