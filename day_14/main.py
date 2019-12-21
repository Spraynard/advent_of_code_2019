from enum import Enum, IntEnum
import itertools
import functools
import math

# class Constituent:
#     def __init__(self, amount, name):
#         self.amount = amount
#         self.name = name

#     def __str__(self):
#         return f"{self.amount} {self.name}"

#     def __repr__(self):
#         return str(self)

#     def __add__(self, other):
#         if self.name != other.name:
#             raise Exception(f"Cannot add constituent of {self.name} and {other.name}")
#         return Constituent(self.amount + other.amount, self.name)

class Reaction:
    def __init__(self, reactants, products):
        self.reactants = reactants
        self.products = products

    def __str__(self):
        return f"({self.reactants}, {self.products})"

    def __repr__(self):
        return str(self)

    # Selectors
    def getReactants(self):
        return self.reactants

    def getProduct(self):
        return self.products

    def getProductName(self):
        return list(self.getProduct().keys())[0]

    def getProductAmount(self):
        return list(self.getProduct().items())[0][1]

    def setProductAmount(self, amount):
        self.products = { self.getProductName() : amount }
        return self.scale(amount)

    # Predicates
    def isBase(self):
        '''
        Test to see if this reaction can be performed with only ORE
        '''
        return "ORE" in self.getReactants() and len(self.reactants) == 1

    def isFuelReaction(self):
        '''
        Test to see if this is the reaction which is used to create fuel
        '''
        return "FUEL" in self.getProduct()

    def produces(self, product):
        '''Does this reaction produce the given product?'''
        return product in self.getProduct()

    def scale(self, amount):
        '''
        Return a reaction in which all the amounts of the reactants are multiplied by given amount
        '''
        reactants = self.getReactants().copy()
        newReactants = []
        for reactant in reactants.items():
            newReactants += [[ reactant[0], reactant[1] * amount ]]

        self.reactants = dict(newReactants)

        return self

    def combineReactants(self, other, product):
        '''
        Returns a new reaction with reactants that have been added together
        '''
        # print("*" * 20)
        # print("COMBINE")
        # print(self)
        # print(other)
        reactants = self.getReactants().copy()

        for reactant in other.getReactants().items():
            constituentName = reactant[0]
            constituentAmount = reactant[1]

            try:
                reactants[constituentName] += constituentAmount
            except KeyError:
                reactants[constituentName] = constituentAmount

        returnReaction = Reaction(reactants, product)
        # print(returnReaction)
        # print("*" * 20)
        return returnReaction

    def copy(self):
        return Reaction(self.getReactants().copy(), self.getProduct().copy())



def createReactantsDictionary( reactants_string ):
    split_reactants = [ reactant.strip() for reactant in reactants_string.split(",") ]
    return { reactant.split(" ")[1] : int(reactant.split(" ")[0]) for reactant in split_reactants }

def createProductsDictionary( products_string ):
    productAmount, productElement = products_string.strip().split(" ")
    return { productElement : int(productAmount) }

class NanoFactory:
    def __init__(self, reaction_list):
        self.reaction_list = reaction_list
        self.reactions = []
        self.reactionsIndex = {}
        self.parse_reaction_list()

    def getReactionThatProduces(self, product):
        if product not in self.reactionsIndex:
            return None

        return self.reactions[self.reactionsIndex[product]].copy()

    def parse_reaction_list(self):
        for index, reaction in enumerate(self.reaction_list.split("\n")):
            reactant_string, products_string = reaction.split("=>")

            parsed_reaction = Reaction(
                createReactantsDictionary(reactant_string),
                createProductsDictionary(products_string)
            )

            self.reactionsIndex[parsed_reaction.getProductName()] = index

            self.reactions += [ parsed_reaction ]


    def convertReactantsTo(self, reactant_name, reaction, surplus={}):
        # print("=" * 20)
        # print("CONVERT")
        # print(reactant_name)
        # print(reaction)
        # print("=" * 20)
        def isFullyBrokenDown(reactant_name, reaction):
            theTruthyTest = []
            for reactant in reaction.getReactants():
                if reactant != reactant_name:
                    result = False

                if self.getReactionThatProduces(reactant).isBase():
                    result = True

                theTruthyTest += [ result ]

            return all(theTruthyTest)

        def combine(a, b):
            return a.combineReactants(b, reaction.getProduct())


        def breakDown(reactant, convertToOre=False):
            '''
            Breaks down a reactant (in the form of a tuple) to a reaction that produces the reactant
            '''
            reactantName = reactant[0]
            reactantAmount = reactant[1]

            if reactantName not in surplus:
                surplus[reactantName] = 0

            '''If we have surplus amount of the reactant we want, use that'''
            while surplus[reactantName] != 0 and reactantAmount != 0:
                surplus[reactantName] -= 1
                reactantAmount -= 1

            if reactantAmount == 0:
                return Reaction({}, {})

            producingReaction = self.getReactionThatProduces(reactantName).copy()
            producingReactionProductAmount = producingReaction.getProductAmount()

            producingReactionScalingFactor = math.ceil(reactantAmount / producingReactionProductAmount)
            scaledProducingReactionAmount = producingReactionScalingFactor * producingReactionProductAmount
            producingReaction.scale(producingReactionScalingFactor)

            reactionSurplus = scaledProducingReactionAmount - reactantAmount


            if producingReaction.isBase() and not convertToOre:
                return Reaction(dict([reactant]), reaction.getProduct())

            # If there's a surplus amount of this product, then
            # print(f"Product Amount {producingReactionProductAmount}")
            # print(f"Reactant Amount {reactantAmount}")
            # print(f"Scaling Factor {producingReactionScalingFactor}")
            # print(f"Scaled Reaction Amount {scaledProducingReactionAmount}")
            # print(f"Reaction Surplus {reactionSurplus}")
            # Put in the surplus amount if the reactantname isn't in the dictionary

            surplus[reactantName] += reactionSurplus

            producingReaction.products = reaction.getProduct()

            return producingReaction

        def breakDownAndCombine(convertToOre=False):
            brokenDownReactions = [ breakDown(reactant, convertToOre) for reactant in reaction.getReactants().items() ]

            reactionWithCombinedConstituents = functools.reduce(
                combine,
                brokenDownReactions,
                Reaction({},{})
            )

            # print("&" * 20)
            # print("BREAK")
            # print(reaction.getReactants().items())
            # print(brokenDownReactions)
            # print("&" * 20)
            return reactionWithCombinedConstituents


        if isFullyBrokenDown(reactant_name, reaction):
            return breakDownAndCombine(True)


        brokenDownReaction = breakDownAndCombine()
        # print(reactionWithCombinedConstituents)

        return self.convertReactantsTo(reactant_name, brokenDownReaction, surplus)


if __name__ == "__main__":
    # with open('ex_1.txt', 'r') as f:
    #     reaction_list = f.read()
    #     nanoFactory = NanoFactory(reaction_list)
    #     test = nanoFactory.getReactionThatProduces('FUEL')
    #     print(nanoFactory.convertReactantsTo('ORE', test))

    # with open('ex_2.txt', 'r') as f:
    #     reaction_list = f.read()
    #     nanoFactory = NanoFactory(reaction_list)
    #     test = nanoFactory.getReactionThatProduces('FUEL')
    #     print(nanoFactory.convertReactantsTo('ORE', test))

    # with open('ex_3.txt', 'r') as f:
    #     reaction_list = f.read()
    #     nanoFactory = NanoFactory(reaction_list)
    #     test = nanoFactory.getReactionThatProduces('FUEL')
        # print(nanoFactory.convertReactantsTo('ORE', test))

    # with open('ex_4.txt', 'r') as f:
    #     reaction_list = f.read()
    #     nanoFactory = NanoFactory(reaction_list)
    #     test = nanoFactory.getReactionThatProduces('FUEL')
    #     print(nanoFactory.convertReactantsTo('ORE', test))

    # with open('ex_5.txt', 'r') as f:
    #     reaction_list = f.read()
    #     nanoFactory = NanoFactory(reaction_list)
    #     test = nanoFactory.getReactionThatProduces('FUEL')
    #     print(nanoFactory.convertReactantsTo('ORE', test))

    with open('ex_3.txt', 'r') as f:
        reaction_list = f.read()
        nanoFactory = NanoFactory(reaction_list)
        test = nanoFactory.getReactionThatProduces('FUEL')
        # print(f"Test {test}")
        test.setProductAmount(655)
        # print(test)
        convertedReaction = nanoFactory.convertReactantsTo('ORE', test)
        # print(convertedReaction)
        # print(list(convertedReaction.getReactants().items()))
        min_fuel = 0
        max_fuel = 10000000000
        ore_target = 1000000000000
        oreAmountThroughConversion = 0
        while abs(max_fuel - min_fuel) > 1 or oreAmountThroughConversion > ore_target:
            fuel_guess = math.floor((max_fuel + min_fuel) / 2)

            reaction = nanoFactory.getReactionThatProduces('FUEL')

            reaction.setProductAmount(fuel_guess)
            convertedReaction = nanoFactory.convertReactantsTo('ORE', reaction)
            oreAmountThroughConversion = convertedReaction.getReactants()['ORE']
            print("*" * 40)
            print(f"abs: {abs(max_fuel - min_fuel)}")
            print(f"min_fuel: {min_fuel}")
            print(f"max_fuel: {max_fuel}")
            print(f"fuel_guess: {fuel_guess}")
            print(oreAmountThroughConversion)
            print("*" * 40)
            if oreAmountThroughConversion < ore_target:
                min_fuel = fuel_guess + 1
            elif oreAmountThroughConversion > ore_target:
                max_fuel = fuel_guess - 1
            else:
                print(oreAmountThroughConversion)
                break
            print(f"New Min_fuel {min_fuel}")
            print(f"New Max Fuel {max_fuel}")
        # for i in range(1,1000000000):
        #     reaction = nanoFactory.getReactionThatProduces('FUEL')
        #     reaction.setProductAmount(i)

        #     convertedReaction = nanoFactory.convertReactantsTo('ORE', reaction)
        #     oreAmountThroughConversion = convertedReaction.getReactants()['ORE']
        #     print(oreAmountThroughConversion)
        #     if oreAmountThroughConversion > 1000000000000:
        #         break
        print(fuel_guess)
