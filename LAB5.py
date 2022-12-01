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
    "nHuman": [400, True, 1, 100],
    "nMosquito": [4000, True, 1, 500],
    "initMosquitoHungry": [0.9, True, 0.0, 1.0],
    "initMosquitoInfected": [0.0, True, 0.0, 1.0],
    "initHumanInfected": [0.2, True, 0.0, 1.0],
    "humanInfectionProb": [0.5, True],
    "mosquitoInfectionProb": [0.5, True, 0.0, 1.0],
    "humanDeathByInfectionProb": [0.003, True, 0.0, 1.0],
    "biteProb": [0.2, True, 0.0, 1.0],
    "mealInterval": [7, True, 1, 100],
    "infectionPeriod": [20, True, 1, 100],
    "immuntiyPeriod": [500, True, 1, 100],
    "humanNaturalDeathProb": [1 / (60 * 365), False],
    "mosquitoNaturalDeathProb": [0.02, False],
}


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

            # save data
            t_list.append(t)
            infection_fractions.append(data[0])

        df["t"] = t_list
        df["infection_fraction"] = infection_fractions

        data_dict[str(value)] = df

    return data_dict


steps = 1000

# effect of population
parameter = "nHuman"
values = [50, 100, 200, 300, 400]

# # effect of pesticide treatment
# parameter = "mosquitoNaturalDeathProb"
# values = [0.001, 0.01, 0.02, 0.03, 0.04]

simulate = True
plot_relation = True

if simulate == True:
    data = parameter_sweep(
        steps=steps,
        init_parameters=parameters,
        parameter=parameter,
        values=values,
    )

    for i, key in enumerate(data.keys()):
        df = data[key]
        df.to_csv("testdata_" + parameter + "_" + key + ".csv")


if plot_relation == True:

    # plot time evolution for each parameter
    for value in values:
        # read data
        df = pd.read_csv(("testdata_" + parameter + f"_{value}.csv"))

        plt.plot(
            df["t"],
            df["infection_fraction"],
            label=parameter + f" = {value}",
            linewidth=0.5,
        )

    plt.xlabel("t")
    plt.ylabel("infection fraction")
    plt.ylim(0, 0.6)
    plt.legend()
    plt.savefig(f"testinfections_over_time_per_{parameter}.png")
    plt.show()

    fraction = float(input("Which fraction of the total simulation is stable? \n"))

    stable_infection_fractions = []
    err_stable_infection_fractions = []

    for value in values:
        # read data
        df = pd.read_csv(("testdata_" + parameter + f"_{value}.csv"))

        # crop df to fraction
        df = df[int((1 - fraction) * len(df)) :]

        # determine mean and error and store values
        stable_infection_fractions.append(np.mean(df["infection_fraction"]))
        err_stable_infection_fractions.append(np.std(df["infection_fraction"]))

    plt.errorbar(
        values,
        stable_infection_fractions,
        yerr=err_stable_infection_fractions,
        fmt="o-",
        capsize=4,
        linewidth=0.5,
    )
    plt.xlabel(parameter)
    plt.ylabel("infection fraction")
    plt.title(
        f"Mean infection fraction when stable: \nfor last {fraction*100}% of {steps} time steps"
    )
    plt.savefig("test" + parameter + "_vs_infection.png")

    plt.show()
