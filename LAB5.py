import malaria_skeleton as malaria


sim = malaria.Model()

# indicate which attributes to store measurements from
attributes = {
    "death_counts": sim.deathCount,
    "infected_counts": sim.infectedCount,
}

measurements = dict.fromkeys(attributes.keys(), [])

for i in range(1000):
    for sim_attribute in attributes.keys():
        sim.update()
        measurements[sim_attribute].append(attributes[sim_attribute])

# print(measurements)
