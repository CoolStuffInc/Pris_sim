# Import necesary modules

%matplotlib inline
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
        if sim ==1 or sim ==0:
            return False
        elif contagion > random.random:
            return True

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
        if random.random > .5:
            row = (self.row + random.choice([1, -1])) % self.grid.size
            col = self.col
        else:
            row = self.row
            col = (self.col + random.choice([1, -1])) % self.grid.size
        # Retrieve neighbor
        neighbor = self.grid.getAgent(row, col)
        # If the agent is influenced, inherit a trait from neighbor
        if self.isInfluenced(neighbor):
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
    row = random.randint(0,grid.size)
    col = random.randint(0,grid.size)
    agent = grid.getAgent(row, col)
    if agent.isPrisonized() == False:
        agent.features.setTrait(0,1)
        x -= 1

# Report starting state
print "Starting prisionization: " + str(grid.getPrisPortion())
print "Loops: " + str(loopCount)

for col in range(grid.size):
    for row in range(grid.size):
        agent = grid.getAgent(row, col)
        print "(" + str(row) + ", " + str(col) + ") " + str(agent.features.curTraits)

# Run the model
iteration = 0
running = True
startTime = millis()
while running:

    # Select a random agent for this model step, then execute the model it
    thisAgent = grid.getAgent(random.randint(0, (grid.size - 1)), random.randint(0, (grid.size - 1)))
    thisAgent.executeModel()
    iteration += 1
    print str(thisAgent.row) + "," + str(thisAgent.col)
    # Only check for equilibrium once in a while to save time
#    if iteration % 10 == 0:
#        if grid.isAtEquilibrium():
#            running = False
    # Temp: 10 iterations
    if iteration > 10:
        running = False

'''
NOTE: There's something wrong with my model, and it's not reaching equilibrium.
I've been interrupting this cell when I run the model.
'''

# Report model results
print "Completion time: " + str((millis() - startTime)) + " milliseconds"
print "Model reached equilibrium after " + str(iteration) + " increments"
print "Ending prisionization: " + str(grid.getPrisPortion())

for col in range(grid.size):
    for row in range(grid.size):
        agent = grid.getAgent(row, col)
        print "(" + str(row) + ", " + str(col) + ") " + str(agent.features.curTraits)
