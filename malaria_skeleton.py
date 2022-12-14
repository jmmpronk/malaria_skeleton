import matplotlib.pyplot as plt
import numpy as np
import malaria_visualize


class Model:
    def __init__(
        self,
        width=50,
        height=50,
        nHuman=10,
        nMosquito=20,
        initMosquitoHungry=0.5,
        initMosquitoInfected=0.2,
        initHumanInfected=0.2,
        humanInfectionProb=0.25,
        mosquitoInfectionProb=0.9,
        humanDeathByInfectionProb=0.3,
        biteProb=1.0,
        mealInterval=5,
        infectionPeriod=3,
        immuntiyPeriod=10,
        humanNaturalDeathProb=0.001,
        mosquitoNaturalDeathProb=0.1,
    ):
        """
        Model parameters
        Initialize the model with the width and height parameters.
        """
        self.height = height
        self.width = width
        self.nHuman = nHuman
        self.nMosquito = nMosquito
        self.initMosquitoHungry = initMosquitoHungry
        self.initMosquitoInfected = initMosquitoInfected
        self.humanInfectionProb = humanInfectionProb
        self.mosquitoInfectionProb = mosquitoInfectionProb
        self.humanDeathByInfectionProb = humanDeathByInfectionProb
        self.biteProb = biteProb
        self.mealInterval = mealInterval
        self.infectionPeriod = infectionPeriod
        self.immunityPeriod = immuntiyPeriod
        self.humanNaturalDeathProb = humanNaturalDeathProb
        self.mosquitoNaturalDeathProb = mosquitoNaturalDeathProb
        # etc.

        """
        Data parameters
        To record the evolution of the model
        """
        self.infectedCount = 0
        self.deathCount = 0
        self.mosquitoDeathCount = 0
        self.immunityCount = 0
        # etc.

        """
        Population setters
        Make a data structure in this case a list with the humans and mosquitos.
        """
        self.humanPopulation = self.set_human_population(initHumanInfected)
        self.mosquitoPopulation = self.set_mosquito_population(
            initMosquitoHungry, initMosquitoInfected
        )

    def set_human_population(self, initHumanInfected):
        """
        This function makes the initial human population, by iteratively adding
        an object of the Human class to the humanPopulation list.
        The position of each Human object is randomized. A number of Human
        objects is initialized with the "infected" state.
        """
        humanPopulation = []
        self.humanPositions = []
        for i in range(self.nHuman):
            x = np.random.randint(self.width)
            y = np.random.randint(self.height)

            """
            Humans may not have overlapping positions.
            """

            # find new position if position is already taken
            while (x, y) in self.humanPositions:
                # print(f"{(x, y)} already in positions {humanPositions}")

                # generate new coordinates
                x = np.random.randint(self.width)
                y = np.random.randint(self.height)

            # store position
            self.humanPositions.append((x, y))

            # determine if human is infected or not
            if (i / self.nHuman) <= initHumanInfected:
                state = "I"  # I for infected
            else:
                state = "S"  # S for susceptible

            # add human instance to list of humans
            humanPopulation.append(Human(x, y, state))

        return humanPopulation

    def set_mosquito_population(self, initMosquitoHungry, initMosquitoInfected):
        """
        This function makes the initial mosquito population, by iteratively
        adding an object of the Mosquito class to the mosquitoPopulation list.
        The position of each Mosquito object is randomized.
        A number of Mosquito objects is initialized with the "hungry" state.
        """
        mosquitoPopulation = []
        for i in range(self.nMosquito):
            x = np.random.randint(self.width)
            y = np.random.randint(self.height)
            if (i / self.nMosquito) <= initMosquitoHungry:
                hungry = True
            else:
                hungry = False

            # determine if mosquito is infected or not
            if np.random.uniform() <= initMosquitoInfected:
                state = True  # True for infected
            else:
                state = False  # False for susceptible
            mosquitoPopulation.append(Mosquito(x, y, hungry, state))
        return mosquitoPopulation

    def update(self):
        """
        Perform one timestep:
        1.  Update mosquito population. Move the mosquitos. If a mosquito is
            hungry it can bite a human with a probability biteProb.
            Update the hungry state of the mosquitos.
        2.  Update the human population. If a human dies remove it from the
            population, and add a replacement human.
        """
        mosquitoInfectedCount = 0

        for i, m in enumerate(self.mosquitoPopulation):
            m.move(self.height, self.width)

            if m.infected:
                mosquitoInfectedCount += 1

            # possibly bite human
            for h in self.humanPopulation:
                if (
                    m.position == h.position
                    and m.hungry
                    and np.random.uniform() <= self.biteProb
                ):
                    m.bite(h, self.humanInfectionProb, self.mosquitoInfectionProb)
                    m.lastMeal = 0

            """
            Set the hungry state from false to true after a
            number of time steps has passed.
            """
            if not m.hungry:
                m.lastMeal += 1
                if (
                    m.lastMeal > self.mealInterval
                ):  # they are very punctual, optional: decay rate probability
                    m.hungry = True
                    m.lastMeal = 0

            if np.random.uniform() <= self.mosquitoNaturalDeathProb:
                """
                Mosquito dies of natural causes.
                """
                self.mosquitoDeathCount += 1
                # print(f"Mosquito {i}: Naturally Dead!")

                x = np.random.randint(self.width)
                y = np.random.randint(self.height)
                if (i / self.nMosquito) <= self.initMosquitoHungry:
                    hungry = True
                else:
                    hungry = False

                self.mosquitoPopulation[i] = Mosquito(x, y, hungry, False)

            # print hunger state of every Mosquito
            # if m.hungry:
            #     hunger_str = "hungry"
            # else:
            #     hunger_str = "satisfied"
            # print(f"Mosquito {i} is {hunger_str}.")

        for j, h in enumerate(self.humanPopulation):
            """
            update the human population.
            """

            if h.state == "I":
                # add infection to the total when human just got infected
                if h.lastInfection == 0:
                    self.infectedCount += 1
                    # print(f"Human {j}: Infected!")

                # end of infection according to normal probability
                if np.random.uniform() <= np.exp(
                    -((h.lastInfection - self.infectionPeriod) ** 2)
                    / np.sqrt(self.infectionPeriod)
                ):
                    # remove from infection count
                    self.infectedCount -= 1

                    # human dies or gets immune
                    if np.random.uniform() <= self.humanDeathByInfectionProb:
                        """
                        Human dies of infection.
                        """
                        self.deathCount += 1
                        # print(f"Human {j}: Dead!")

                        x = np.random.randint(self.width)
                        y = np.random.randint(self.height)

                        while (x, y) in self.humanPositions:
                            x = np.random.randint(self.width)
                            y = np.random.randint(self.height)

                        self.humanPopulation[j] = Human(x, y, state="S")

                    else:
                        """
                        Human is immune
                        """
                        h.state = "Immune"
                        # print(f"Human {j}: Immune!")
                        h.lastImmunity = 0
                        self.immunityCount += 1
                else:
                    # add time to last infection
                    h.lastInfection += 1

            elif h.state == "Immune":
                h.lastImmunity += 1

                # also according decay rate probability
                if np.random.uniform() <= np.exp(
                    -((h.lastImmunity - self.immunityPeriod) ** 2)
                    / np.sqrt(self.immunityPeriod)
                ):
                    self.immunityCount -= 1
                    h.state = "S"
                    # print(f"Human {j}: Susceptible!")

            if np.random.uniform() <= self.humanNaturalDeathProb:
                """
                Human dies of natural causes.
                """
                self.deathCount += 1
                if h.state == "I":
                    self.infectedCount -= 1
                elif h.state == "Immune":
                    self.immunityCount -= 1
                # print(f"Human {j}: Naturally Dead!")

                # give birth to new human on new free position
                x = np.random.randint(self.width)
                y = np.random.randint(self.height)

                while (x, y) in self.humanPositions:
                    x = np.random.randint(self.width)
                    y = np.random.randint(self.height)

                self.humanPopulation[j] = Human(x, y, state="S")

        """
        To implement: update the data/statistics e.g. infectedCount,
                      deathCount, etc.
        """
        return (
            self.infectedCount / self.nHuman,
            mosquitoInfectedCount / self.nMosquito,
            self.deathCount,
            self.mosquitoDeathCount,
            self.immunityCount / self.nHuman,
        )


class Mosquito:
    def __init__(self, x, y, hungry, state):
        """
        Class to model the mosquitos. Each mosquito is initialized with a random
        position on the grid. Mosquitos can start out hungry or not hungry.
        All mosquitos are initialized infection free (this can be modified).
        """
        self.position = [x, y]
        self.hungry = hungry
        self.infected = state
        self.lastMeal = 0  # time since last meal

    def bite(self, human, humanInfectionProb, mosquitoInfectionProb):
        """
        Function that handles the biting. If the mosquito is infected and the
        target human is susceptible, the human can be infected.
        If the mosquito is not infected and the target human is infected, the
        mosquito can be infected.
        After a mosquito bites it is no longer hungry.
        """
        if self.infected and human.state == "S":
            if np.random.uniform() <= humanInfectionProb:
                human.state = "I"
                human.lastInfection = 0
        elif not self.infected and human.state == "I":
            if np.random.uniform() <= mosquitoInfectionProb:
                self.infected = True
        self.hungry = False

    def move(self, height, width):
        """
        Moves the mosquito one step in a random direction.
        """
        deltaX = np.random.randint(-1, 2)
        deltaY = np.random.randint(-1, 2)
        """
        To implement: the mosquitos may not leave the grid. There are two
                      options:
                      - fixed boundaries: if the mosquito wants to move off the
                        grid choose a new valid move.
                      - periodic boundaries: implement a wrap around i.e. if
                        y+deltaY > ymax -> y = 0.
        """
        self.position[0] = (self.position[0] + deltaX) % width
        self.position[1] = (self.position[1] + deltaY) % height


class Human:
    def __init__(self, x, y, state):
        """
        Class to model the humans. Each human is initialized with a random
        position on the grid. Humans can start out susceptible or infected
        (or immune).
        """
        self.position = [x, y]
        self.state = state
        self.lastInfection = 0  # time since last infection
        self.lastImmunity = 0  # time since last immunity


if __name__ == "__main__":
    """
    Simulation parameters
    """
    fileName = "simulation"
    timeSteps = 1000
    t = 0

    # whether or not to run simulations and/or plot
    runSim = True
    plotData = True

    if runSim:
        """
        Run a simulation for an indicated number of timesteps.
        """
        file = open(fileName + ".csv", "w")
        sim = Model(
            width=50,
            height=50,
            nHuman=400,
            nMosquito=500,
            initMosquitoHungry=0.9,
            initMosquitoInfected=0,
            initHumanInfected=0.2,
            humanInfectionProb=0.5,
            mosquitoInfectionProb=0.5,
            humanDeathByInfectionProb=0.2,
            biteProb=0.9,
            mealInterval=3,
            infectionPeriod=20,
            immuntiyPeriod=20,
            humanNaturalDeathProb=0.001,
            mosquitoNaturalDeathProb=0.01,
        )
        vis = malaria_visualize.Visualization(sim.height, sim.width)

        print("Starting simulation")
        while t < timeSteps:
            data = sim.update()  # Catch the data
            line = (
                str(t)
                + ","
                + str(data[0])
                + ","
                + str(data[1])
                + ","
                + str(data[2])
                + ","
                + str(data[3])
                + ","
                + str(data[4])
                + "\n"
            )  # Separate the data with commas
            file.write(line)  # Write the data to a .csv file
            if t % 100 == 0:
                print(f"t = {t}")
                vis.update(t, sim.mosquitoPopulation, sim.humanPopulation)
            t += 1
        file.close()
        vis.persist()

    if plotData:
        """
        Make a plot by from the stored simulation data.
        """
        data = np.loadtxt(fileName + ".csv", delimiter=",")
        time = data[:, 0]
        infectedCount = data[:, 1]
        mosquitoInfectedCount = data[:, 2]
        deathCount = data[:, 3]
        mosquitoDeathCount = data[:, 4]
        immunityCount = data[:, 5]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=[12, 12])
        ax1.plot(time, infectedCount, label="human infection fraction")
        ax1.plot(time, immunityCount, label="human immunity fraction")
        ax3.plot(time, mosquitoInfectedCount, label="mosquito infection fraction")
        ax2.plot(time, deathCount, label="human deaths")
        ax4.plot(time, mosquitoDeathCount, label="mosquito deaths")
        ax1.legend()
        ax2.legend()
        ax3.legend()
        ax4.legend()
        plt.savefig("Simulation_statistics.png")
        plt.show()
