'''
Prisionization contagion simulator
'''

# Import necesary modules
import random
import time
import numpy

# Helper function for getting the current time in milliseconds
millis = lambda: int(round(time.time() * 1000))

'''
General model parameters
'''
gridSize = 10
prisPct = 0.2
# features = 10
# traits = 5
# contagion = 0.75
# decay = 0.2
# incar = 0.1

'''
Features class:
    Static vars:
        * count - number of features to be modeled.
        * traitCounts - an array with length equal to the feature count. Each
            element holds an integer representing the number of possible traits
            for the corresponding feature.

    Object vars:
        * curTraits - an array with length equal to the feature count. Each
            element holds the current trait value for the corresponding feature.
            For the purposes of this model, curTraits[0] represets the binary
            trait for the prisionaization feature.

    Static methods:
        * init(iraitCounts, prisPct) - sets the feature count, traitCounts,
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
        self.setTrait(0, 0)

    def randomizeTraits(self):
        for i in range(Features.count - 1):
            self.curTraits[i] = random.randint(0, self.traitCounts[i]-1)

    def setTrait(self, which, val):
        self.curTraits[which] = val

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
        neighbors = [grid.getAgent(r+1, c+1), grid.getAgent(r-1, c-1), \
            grid.getAgent(r+1, c-1), grid.getAgent(r-1, c+1)]
        # Influence is possible if similarity to any neighbor is between 0 and 1
        for i in range(len(neighbors)):
            similarity = self.similarity(neighbors[i])
            if similarity > 0 and similarity < 1:
                return True
        return False

    def isInfluenced(self, neighbor):
        sim = self.similarity(neighbor)
        if sim == 1 or sim == 0:
            return False
        return True if random.random() <= sim else False

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
        row = self.row + random.choice([1, -1])
        col = self.col + random.choice([1, -1])
        # Retrieve neighbor
        neighbor = self.grid.getAgent(row, col)
        # If the agent is influenced, inherit a trait from neighbor
        if self.isInfluenced(neighbor):
            self.inheritTrait(neighbor)

'''
Grid class:
    Object vars:
        * size - the heigh / width of the grid
        * agents - a 2D matrix where each element contains an agent
        * getLocationCount - returns the total number of elements in the
            agents matrix

    Object methods:
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
        # If the requested location is off the edge of the grid, wrap
        # around to the other edge
        if row < 0:
            row = grid.size - 1
        elif row > grid.size - 1:
            row = 0
        if col < 0:
            col = grid.size - 1
        elif col > grid.size - 1:
            col = 0
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

# Report starting state
counter = round(grid.getLocationCount() * prisPct)
loops = 0
while counter > 0:
    loops += 1
    row = random.randint(0, grid.size)
    col = random.randint(0, grid.size)
    agent = grid.getAgent(row, col)
    if agent.isPrisonized() == False:
        agent.features.setTrait(0, 1)
        counter -= 1

print "Loop count: " + str(loops)
print "Starting prisionization: " + str(grid.getPrisPortion())

# Run the model
iteration = 0
running = True
startTime = millis()
while running:
    # Select a random agent for this model step, then execute the model it
    thisAgent = grid.getAgent(random.randint(0, (grid.size - 1)), \
        random.randint(0, (grid.size - 1)))
    thisAgent.executeModel()
    iteration += 1
    # Only check for equilibrium once in a while to save time
    if iteration % 10 == 0:
        if grid.isAtEquilibrium():
            running = False

# Report model results
print "Completion time: " + str(millis() - startTime) + " milliseconds"
print "Model reached equilibrium after " + str(iteration) + " increments"
print "Ending prisionization: " + str(grid.getPrisPortion())
