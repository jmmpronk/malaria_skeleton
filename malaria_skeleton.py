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
        initHumanInfected=0.2,
        humanInfectionProb=0.25,
        mosquitoInfectionProb=0.9,
        biteProb=1.0,
        mealInterval=5,
        infectionPeriod=3,
        immuntiyPeriod=10,
        humanDeathByInfectionProb=0.3,
    ):
        """
        Model parameters
        Initialize the model with the width and height parameters.
        """
        self.height = height
        self.width = width
        self.nHuman = nHuman
        self.nMosquito = nMosquito
        self.humanInfectionProb = humanInfectionProb
        self.mosquitoInfectionProb = mosquitoInfectionProb
        self.biteProb = biteProb
        self.mealInterval = mealInterval
        self.infectionPeriod = infectionPeriod
        self.immunityPeriod = immuntiyPeriod
        self.humanDeathByInfectionProb = humanDeathByInfectionProb
        # etc.

        """
        Data parameters
        To record the evolution of the model
        """
        self.infectedCount = 0
        self.deathCount = 0
        self.immunityCount = 0
        # etc.

        """
        Population setters
        Make a data structure in this case a list with the humans and mosquitos.
        """
        self.humanPopulation = self.set_human_population(initHumanInfected)
        self.mosquitoPopulation = self.set_mosquito_population(initMosquitoHungry)

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

    def set_mosquito_population(self, initMosquitoHungry):
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
            mosquitoPopulation.append(Mosquito(x, y, hungry))
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
        for i, m in enumerate(self.mosquitoPopulation):
            m.move(self.height, self.width)

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
                    print("Infected!")

                if h.lastInfection > self.infectionPeriod:
                    if np.random.uniform() <= self.humanDeathByInfectionProb:
                        """
                        Human dies
                        """
                        self.deathCount += 1
                        print("Dead!")

                        self.humanPositions[j] = ()

                        # human reincarnates on same position

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
                        print("Immunity!")
                        h.lastImmunity = 0
                        self.immunityCount += 1
                else:
                    # add time to last infection
                    h.lastInfection += 1

            elif h.state == "Immune":
                h.lastImmunity += 1
                if h.lastImmunity > self.immunityPeriod:
                    h.state = "S"
                    print("Susceptible!")

            ## to implement: human dies of natural causes

        """
        To implement: update the data/statistics e.g. infectedCount,
                      deathCount, etc.
        """
        return self.infectedCount, self.deathCount, self.immunityCount


class Mosquito:
    def __init__(self, x, y, hungry):
        """
        Class to model the mosquitos. Each mosquito is initialized with a random
        position on the grid. Mosquitos can start out hungry or not hungry.
        All mosquitos are initialized infection free (this can be modified).
        """
        self.position = [x, y]
        self.hungry = hungry
        self.infected = False
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
    timeSteps = 40
    t = 0

    # whether or not to run simulations and/or plot
    runSim = True
    plotData = False

    if runSim:
        """
        Run a simulation for an indicated number of timesteps.
        """
        file = open(fileName + ".csv", "w")

        sim = Model(
            width=20,
            height=20,
            nHuman=10,
            nMosquito=20,
            initHumanInfected=1,
            mosquitoInfectionProb=1,
            humanDeathByInfectionProb=0.75,
            initMosquitoHungry=1,
            infectionPeriod=10,
        )

        vis = malaria_visualize.Visualization(sim.height, sim.width)

        print("Starting simulation")
        while t < timeSteps:
            # print(t)
            [d1, d2, d3] = sim.update()  # Catch the data
            line = (
                str(t) + "," + str(d1) + "," + str(d2) + "\n"
            )  # Separate the data with commas
            file.write(line)  # Write the data to a .csv file
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
        deathCount = data[:, 2]
        plt.figure()
        plt.plot(time, infectedCount, label="infected")
        plt.plot(time, deathCount, label="deaths")
        plt.legend()
        plt.show()
