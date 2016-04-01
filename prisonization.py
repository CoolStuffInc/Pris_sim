# Import necesary modules

#%matplotlib inline
import random
import time
import matplotlib.pyplot as plt
import numpy
# import seaborn; seaborn.set()

# Helper function for getting the current time in seconds
millis = lambda: int(round(time.time()*1000))

'''
Features class:
    Static vars:
        * traitCounts - an array with length equal to the feature count. Each
            element holds an integer representing the number of possible traits
            for the corresponding feature.

    Object vars:
        * curTraits - an array with length equal to the feature count. Each
            element holds the current trait value for the corresponding feature.
            For the purposes of this model, curTraits[0] represets the binary
            trait for the prisionization feature.

    Static methods:
        * init(traitCounts, prisPct) - sets the feature count, traitCounts,
            and initial relative prisionization.

    Object methods:
        * randomizeTraits - sets random traits for each feature in the object
        * setTrait - sets the trait of a selected feature.
'''
class Features(object):

    # Initialize the feature count and the trait ranges for those features
    @staticmethod
    def init(traitCounts):
        Features.count = len(traitCounts)
        Features.traitCounts = traitCounts

    def __init__(self):
        # Initialize an empty array with a location for each current trait
        self.curTraits = [0 for i in range(Features.count)]
        self.randomizeTraits()
        self.setTrait(0,0)

    def randomizeTraits(self):
        for i in range(1, Features.count):
            self.curTraits[i] = random.randint(0, self.traitCounts[i]-1)

    def setTrait(self, which, val):
        self.curTraits[which] = val

'''
Agent class:
    Object vars:
        * grid - a reference to the grid in which the agent is located
        * row - row of the grid in which the agent is located
        * col - column of the grid in which the agent is located
        * features - the features object

    Object methods:
        * printTraits - prints to console the current traits for this agent
        * influencePossible - returns a boolean value indicating whether the
            agent could be influenced by any of its neighbors
        * isInfluenced(neighbor) - returns a boolean value indicating whether
            a new interaction with a given neighbor causes the agent to be
            influenced
        * isPrisonized - returns a boolean value indicating whether the agent
            is currently prisionized
        * similarity(neighbor) - returns a similarity index from 0.0 to 1.0
            indicating the agent's cultural similarity to the given neighbor
        * differingTraits(neighbor) - returns an array containing values of the
            features for which the agent and the given neighbor do not share
            the same trait
        * inheritTrait(neighbor) - causes the agent to inherit a randomly
            selected feature trait from the given neighbor
        * executeModel - selects a random neighbor, tests whether the agent
            is influenced, and if it is, causes the agent to inherit a trait
            from that neighbor
'''
class Agent(object):

    def __init__(self, row, col, grid):
        self.grid = grid
        self.row = row
        self.col = col
        self.features = Features()

    def printTraits(self):
        print self.features.curTraits

    def influencePossible(self):
        # Get all neighbors
        r = self.row
        c = self.col

        neighbors = [grid.getAgent((r+1) % self.grid.size, c), grid.getAgent((r-1) % self.grid.size, c), \
            grid.getAgent(r, (c-1) % self.grid.size), grid.getAgent(r, (c+1) % self.grid.size)]

        # Influence is possible if similarity to any neighbor is between 0 and 1
        for i in range(len(neighbors)):
            similarity = self.similarity(neighbors[i])
            if similarity > 0 and similarity < 1:
                return True
        return False

    def isInfluenced(self, neighbor):
        sim = self.similarity(neighbor)
        print "Similarity: " + str(sim)
        if sim ==1 or sim ==0:
            return False
        if contagion > random.random():
            print "Contagisized"
            return True
        else:
            print "Not contagisized"
            return False

    def isPrisonized(self):
        return True if self.features.curTraits[0] == 1 else False

    def similarity(self, neighbor):
        matchingTraits = 0
        for x in range (Features.count):
            if self.features.curTraits[x] == neighbor.features.curTraits[x]:
                matchingTraits += 1
        return float(matchingTraits) / Features.count

    def differingTraits(self, neighbor):
        diffTraits = []
        for x in range (Features.count):
            if self.features.curTraits[x] != neighbor.features.curTraits[x]:
                diffTraits.append(x)
        return diffTraits

    def inheritTrait(self, neighbor):
        which = random.choice(self.differingTraits(neighbor))
        self.features.curTraits[which] = neighbor.features.curTraits[which]

    def executeModel(self):
        # Pick a neighbor location
        # I changed this to use NSEW neighbors, and to wrap around the grid
        if random.random() > .5:
            row = (self.row + random.choice([1, -1])) % self.grid.size
            col = self.col
        else:
            row = self.row
            col = (self.col + random.choice([1, -1])) % self.grid.size
        # Retrieve neighbor
        neighbor = self.grid.getAgent(row, col)
        print "A : " + str(self.row) + ", " + str(self.col) + " N: " + str(row) + ", " + str(col)
        # If the agent is influenced, inherit a trait from neighbor
        print "Checking influence"
        if self.isInfluenced(neighbor):
            print "Agent is inheriting trait"
            self.inheritTrait(neighbor)

'''
Grid class:
    Object vars:
        * size - the height / width of the grid
        * agents - a 2D matrix where each element contains an agent

    Object methods:
        * getLocationCount - returns the total number of elements in the
            agents matrix
        * addAgent(row, col) - adds a new agent at the specified matrix location
        * getAgent(row, col) - returns the agent object from the specified
            matrix location
        * getPrisPortion - returns a value from 0.0 to 1.0 representing the
            portion of the total grid population that is currently prisionized
        * isAtEquilibrium - returns a boolean value indicating whether the
            grid object is currently at equilibrium (this occurs when every
            agent in the grid either completly shares the culture of all its
            neighbors or shares no culture with its neighbors)
'''
class Grid(object):

    def __init__(self, size):
        self.agents = [[0 for x in range(size)] for x in range(size)]
        self.size = size

    def getLocationCount(self):
        count = self.size * self.size
        return count

    def addAgent(self, row, col):
        self.agents[row][col] = Agent(row, col, self)

    def getAgent(self, row, col):
        return self.agents[row][col]

    def getPrisPortion(self):
        prisPop = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.getAgent(x, y).isPrisonized():
                    prisPop += 1
        return float(prisPop) / self.getLocationCount()

    def isAtEquilibrium(self):
        for x in range(self.size):
            for y in range(self.size):
                if(self.getAgent(x, y).influencePossible()):
                    return False
        return True

def printSimilarities():
    for row in range(grid.size):
        for col in range(grid.size):
            agent = grid.getAgent(row, col)
            # print "(" + str(row) + ", " + str(col) + ") " + str(agent.features.curTraits)
            print agent.similarity(grid.getAgent(row, (col+1) % grid.size))
            print agent.similarity(grid.getAgent((row+1) % grid.size , col))

def printFeatures():
    for row in range(grid.size):
        for col in range(grid.size):
            agent = grid.getAgent(row, col)
            print str(row) + ", " + str(col) + " " + str(agent.features.curTraits)


# Parameters
gridSize = 3
prisPct = 0.2
contagion = 1

'''
Set the possible trait counts for the features. In this case, prisionization
is binary while the other features have some other abitrary number of traits
associated with them.
'''
traitCounts = [2,3,3,3]

'''
Initialize the features class with the number of different traits for each of
the features and the initial relative prisionization rate.
'''
Features.init(traitCounts)

# Initialize the grid size, add agents
grid = Grid(gridSize)
for x in range(grid.size):
    for y in range(grid.size):
        grid.addAgent(x, y)

# Assign initial prisionization
x = round(prisPct*grid.getLocationCount())
loopCount = 0
while x > 0:
    loopCount += 1
    row = random.randint(0,grid.size-1)
    col = random.randint(0,grid.size-1)
    agent = grid.getAgent(row, col)
    if agent.isPrisonized() == False:
        agent.features.setTrait(0,1)
        x -= 1

# Report starting state
print "Starting prisionization: " + str(grid.getPrisPortion())
print "Loops: " + str(loopCount)

# printSimilarities()
printFeatures()

# Run the model
iteration = 0
running = True
startTime = millis()
while running:
    print "Time step " + str(iteration)
    # Select a random agent for this model step, then execute the model it
    thisAgent = grid.getAgent(random.randint(0, (grid.size - 1)), random.randint(0, (grid.size - 1)))
    thisAgent.executeModel()
    iteration += 1
    # printSimilarities()
    printFeatures()
    # print str(thisAgent.row) + "," + str(thisAgent.col)
    # Only check for equilibrium once in a while to save time
    if iteration % 10 == 0:
        if grid.isAtEquilibrium():
            running = False
    if iteration > 1000:
        running = False


'''
NOTE: There's something wrong with my model, and it's not reaching equilibrium.
I've been interrupting this cell when I run the model.
'''

# Report model results
print "Completion time: " + str((millis() - startTime)) + " milliseconds"
print "Model reached equilibrium after " + str(iteration) + " increments"
print "Ending prisionization: " + str(grid.getPrisPortion())

# printSimilarities()
printFeatures()

# for col in range(grid.size):
#     for row in range(grid.size):
#         agent = grid.getAgent(row, col)
#         # print "(" + str(row) + ", " + str(col) + ") " + str(agent.features.curTraits)
#         neighbor0 = grid.getAgent(row, (col-1))
#         neighbor1 = grid.getAgent((row-1) , col)
#         simArray[row+1][col] = agent.similarity(neighbor0)
#         simArray[row][col+1] = agent.similarity(neighbor1)
#
# for row in range(0,len(simArray)):
#     vector = simArray[row]
#     print vector

# for col in range(grid.size):
#     for row in range(grid.size):
#         agent = grid.getAgent(row, col)
#         print "(" + str(row) + ", " + str(col) + ") " + str(agent.features.curTraits)
