import numpy as np
import random
from logger import loguru
from random import randrange
import argparse
import numpy.random.exponential as Exponential

'''
This is an implementation of the Susceptible, Infected, Recovered model for 02-718.

Simon Levine-Gottreich, 2020

Ex: SRI_discrete.py --m 100 --n 1000 --k 10 --lambdas 1,1,0
'''

def main(args):
    args = parser.parse_args()
    simulate(args)


def CTMM(world:World):

    '''Run a continuous time markov model based on
    an initialized World object'''

    t=0
    while world.sum_of_infected !=0:
        for i in range(world.m):

            world.countries[i].update_rate_of_infection() #get rates
            world.countries[i].update_rate_of_recovery()
            world.countries[i].update_rate_of_migration_out()

            world.countries[i].sample_t_infection() #get t_x = Exp(rates)
            world.countries[i].sample_t_recovery()  
            world.countries[i].sample_t_migration_out()

            t_min = np.min(
                world.countries[i].t_i,
                world.countries[i].t_r,
                world.countries[i].t_m,
            )

            if world.countries[i].t_i == t_min:
                world.new_infection(world.countries[i])

            elif world.countries[i].t_r == t_min:
                world.new_recovery(world.countries[i])

            elif world.countries[i].t_m == t_min:
                #randomly select a destination country for migration...
                j = np.random.choice(np.setdiff1d(range(world.m), i))
                world.new_migration(world.countries[i],world.countries[j])
                    #will push numbers to/from respective countries, s.t.
                    # country i has uniform probability of migration from S,I, or R.
                    # country j, chosen at random (uniform)

            t+=t_min
        

        world.update_sum_of_infected()



class World:
    def __init__(self, m, N, k, l1_0, l2, l3):

        self.m = m
        # initialize countries
        self.countries = [Country(N,k,l1_0,l2,l3) for _ in range(self.m)]
        self.sum_of_infected = np.sum([c.I for c in self.countries])

    
    def new_infection(self, country_i:Country):
        country_i.new_infection()
    def new_recovery(self, country_i: Country):
        country_i.new_recovery()

    def new_migration(self, country_i:Country, country_j:Country):
        #migrate, and assume a uniform distribution across
        # S,I,and R groups for who will migrate...

        subpopulations_i = [country_i.S,country_i.I,country_i.R]
        able_to_migrate_i = [p!=0 for p in subpopulations_i] #1,0,1 , for ex.

        choice_i_idx = randrange(len(able_to_migrate_i))
        choice_i = able_to_migrate_i[choice_i_idx]

        while choice_i == 0:
            # take a random person from a group that actually
            # still has people!
            del able_to_migrate_i[choice_i_idx] #remove from consideration
            choice_i_idx = randrange(len(able_to_migrate_i)) #resample
            choice_i = able_to_migrate_i[choice_i_idx] #choose new subpopulation from N = S,I, or R.

        if choice_i_idx == 0:
            country_i.S -= 1
            country_j.S += 1
        elif choice_i_idx == 1:
            country_i.I -= 1
            country_j.I += 1
        elif choice_i_idx == 2:
            country_i.R -= 1
            country_j.R += 1

    def update_sum_of_infected(self):
        self.sum_of_infected = np.sum([c.I for c in self.countries])
    
class Country:
    # make one country i, for 1...i...m
    def __init__(self, N,k,l_1_0,l_2,l3):

        self.N = N

        #initialize parameters
        self.S = N-k
        self.I = k
        self.R = 0

        self.l1 = np.random.uniform(low=0.0,high=l_1_0)
        self.l2 = l2
        self.l3 = l3
        
        # I will compute rates of infection first during an the initial CTMM iteration
        # since a country may have migrants on its first round, changing these values.

        self.rate_of_infection = None #self.l1*self.I*(self.S/self.R)
        self.rate_of_recovery =  None #self.l2*I
        self.rate_of_migration_out = None # self.l3*N

        self.t_i = None
        self.t_r = None
        self.t_m = None

    def new_infection(self):
        self.S -= 1
        self.I += 1

    def new_recovery(self):
        self.I -= 1
        self.R += 1

    def update_rate_of_infection(self):
        self.rate_of_infection = self.l1*self.I*(self.S/self.R)
    def update_rate_of_recovery(self):
        self.rate_of_recovery = self.l2*self.I
    def update_rate_of_migration_out(self):
        self.rate_of_migration_out = self.l3*self.N

    def sample_t_infection(self):
        self.t_i=Exponential((1/self.rate_of_infection)) #numpy uses scaling param 1/beta
    def sample_t_recovery(self):
        self.t_r = Exponential((1/self.rate_of_recovery))
    def sample_t_migration_out(self):
        self.t_m = Exponential((1/self.rate_of_migration_out))




parser = argparse.ArgumentParser(
    description='Process (m, N, k, l1, l2, l3) args for CTMM (discrete SRI).'
    )

parser.add_argument(
        "--m",
        default=100,
        type=int,
        )

parser.add_argument(
        "--N",
        default=1000,
        type=float,
        )

parser.add_argument(
        "--k",
        default=10,
        type=int,
        )

parser.add_argument(
        "--l1",
        default=2.,
        type=float,
        )

parser.add_argument(
        "--l2",
        default=1.,
        type=float,
        )

parser.add_argument(
        "--l3",
        default=0.,
        type=float,
        )
        
        
args = parser.parse_args()

if __name__=="__main__":
    main(args)

