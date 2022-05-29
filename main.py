import time
import random
from osbrain import Agent, run_nameserver, run_agent

TOPICS = ['Food', 'Movies', 'Sport', 'Traveling', 'Music', 'Games', 'Books']
NAMES = ['Marie', 'John', 'Nicolas', 'Paul', 'Martha', 'Natalie', 'Matt']


class SpeedDateOrganizer(Agent):
    pairs = []

    def on_init(self):
        print("The Speeddating event has begun!")
        self.hasEnded = False

    def shuffle_pairs(self):
        print('Changing the pairs...')
        random.shuffle(pairs)
        self.send('OrganizerChannel', self.pairs)


class DateResponder(Agent):
    def on_init(self):
        self.Name = random.choice(NAMES)
        self.topics = random.sample(TOPICS, 2)
        print("DateResponder " + self.Name + " initiated with topics: " + str(self.topics))

    def set_address(self, id):
        self.set_attr(address=self.bind('REP', str(id), handler=self.answer_question))
        return self.address

    def answer_question(self, msg):
        if msg in self.topics:
            return 'yes'
        return 'no'


class DateInitiator(Agent):

    def on_init(self):
        self.Name = random.choice(NAMES)
        self.topics = random.sample(TOPICS, 2)
        print("DateInitiator " + self.Name + " initiated with topics: " + str(self.topics))

def start_date(agent, pairs):
    table = pairs[agent.id]
    index = random.randint(0, 1)
    agent.send(str(table), agent.topics[index])
    response = agent.recv(str(table))
    if response == 'yes':
        agent.send('report', agent.Name + " Found love of his/her life because of interest: " + agent.topics[index])

def end_event(agent, message):
    print(message)
    agent.hasEnded = True

if __name__ == '__main__':
    # Init variables
    nameServer = run_nameserver()
    responders = []
    initiators = []
    addresses = []
    noOfPairs = 5

    # shuffle initial pairs
    pairs = []
    for i in range(noOfPairs):
        pairs.append(i)
    random.shuffle(pairs)

    # init organizer
    organizer = run_agent('Organizer', base=SpeedDateOrganizer)
    organizer.set_attr(pairs=pairs)
    addressToSubscribe = organizer.bind('PUB', alias='OrganizerChannel')

    # init participants
    for i in range(noOfPairs):
        # Responders
        responder = run_agent('Responder' + str(i), base=DateResponder)
        responder.set_attr(id=i)
        responders.append(responder)
        responder.set_address(i)
        addresses.append(responder.get_attr('address'))

        # Initiators
        initiator = run_agent('Initiator' + str(i), base=DateInitiator)
        initiator.set_attr(id=i)
        initiators.append(initiator)
        address = initiator.bind('PUSH', alias='report')
        organizer.connect(address, handler=end_event)
        initiator.connect(addressToSubscribe, handler=start_date)
    # connect each initiator to each responder address
    for agent in initiators:
        for i in range(len(addresses)):
            agent.connect(addresses[i], alias=str(i))

    # main loop
    while not organizer.get_attr('hasEnded'):
        organizer.shuffle_pairs()
        time.sleep(3)
    nameServer.shutdown()