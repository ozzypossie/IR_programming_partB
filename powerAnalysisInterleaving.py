from itertools import permutations
import random
from copy import deepcopy
import numpy as np
from scipy.stats import norm
import math

##############################################
### OFFLINE EVALUATION
##############################################

def compute_ERR(list):
    """
    Outputs the ERR measure of the rankinglist ([doc_id1, doc_id2, doc_id3]).
    """
    ERR = 0
    for r in range(len(list)):
        theta_r = compute_click_probability(get_relevance(list[r]))
        prod = 1
        for i in range(r):
            prod *= (1-compute_click_probability(get_relevance(list[i])))
        ERR += prod*theta_r*1/(r+1)
    return ERR

def compute_click_probability(rel):
    """
    Outputs the click-probability theta.
    """
    rel_max = 1
    return (2**rel - 1)/2**rel_max

def create_ranking_pairs():
    """
    TODO: maybe we want to exclude some pairs?
    Outputs a list of tuples with all possible ranking pairs from a pool of 12 document ids.
    """
    list_of_pairs = []
    perm = list(permutations(range(12),3))
    for i in perm:
        for j in perm:
            pair = (list(i),list(j))
            list_of_pairs.append(pair)
    return list_of_pairs

def get_relevance(doc):
    """
    Outputs the relevance of the document, given as integer.
    """
    if (doc<0 or doc>11):
        raise Exception('Document id should be from 0 to 12!')

    if doc<6:
        return 0
    else:
        return 1

def divide_pairs_over_bins(list_pairs):
    """
    Divides a list of pairs over 10 bins according to the delta ERR.
    """
    dERRs = [[] for i in range(10)]
    for i in list_pairs:
        deltaERR = compute_ERR(i[0]) - compute_ERR(i[1])
        #Keep all the positive delta ERRs and put them in the respective bin
        if deltaERR > 0:
            if deltaERR < 0.1:
                dERRs[0].append(i)
            else:
                bin = str(deltaERR*10)
                dERRs[int(bin[0])].append(i)
    return dERRs

# TODO: Uncomment lines
# pairs = create_ranking_pairs() #list of all distinct ranking pairs
# deltaERRs = divide_pairs_over_bins(pairs) #list of all pairs (tuples of two lists) divided over the 10 bins

## For testing purposes:
#lst = [7, 8, 9]
#print(compute_ERR(lst))

#print(divide_pairs_over_bins([([3,5,7],[1,2,3]),([6,8,11],[3,2,0]),([3,5,8],[1,2,3])]))

##############################################
### ONLINE EVALUATION
##############################################

## Interleaving

def coin_to_ranker(cointoss):
    if (cointoss == 0):
        return "E"
    if (cointoss == 1):
        return "P"
    else:
        raise Exception('This number should be either 0 or 1!')

def td_interleave(pair):
    # Writing the pair as a list makes it mutable, which makes the rest easier to code.
    # If we do not want the original pair to be changed, we need to do a deepcopy
    new_pair = deepcopy(list([pair[0], pair[1]]))
    result = []
    for i in range(3):
        cointoss = random.randint(0, 1)
        result += [(new_pair[cointoss][0], coin_to_ranker(cointoss))]
        if (new_pair[cointoss][0] in new_pair[1 - cointoss]):
            new_pair[1 - cointoss].remove(new_pair[cointoss][0])
        new_pair[cointoss] = new_pair[cointoss][1:]
    return result

# The softmax takes the rank of a document as well as the maximal rank and returns
# the probability of choosing that document
def softmax(r, max_r):
    tau = 3
    ranks = range(1,max_r+1)
    normalizer = sum([rank**(-tau) for rank in ranks])
    return r**(-tau)/normalizer

def pr_interleave(pair):
    # Writing the pair as a list makes it mutable, which makes the rest easier to code.
    # If we do not want the original pair to be changed, we need to do a deepcopy
    new_pair = deepcopy(list([pair[0], pair[1]]))
    result = []
    sm = [[],[]]
    sm[0] = [softmax(r, 3) for r in range(1, 4)]
    sm[1] = [softmax(r, 3) for r in range(1, 4)]
    population = [[0, 1, 2], [0, 1, 2]]
    for i in range(3):
        cointoss = random.randint(0, 1)
        index = random.choices(population[cointoss], sm[cointoss])[0]
        sm[cointoss][index] = 0
        result += [(new_pair[cointoss][index], coin_to_ranker(cointoss))]
        for j in range(3):
            if (new_pair[cointoss][index] == new_pair[1 - cointoss][j]):
                sm[1 - cointoss][j] = 0       
    return result



## Simulating user clicks
def yandex_log_parser():
    """
    This function parses the Yandex Click Log File and yields which ranks are clicked in a session.
    """
    sessionID = 0
    links = [-1 for i in range(10)] #dummy list
    clicks = [0 for i in range(10)]
    list_clicks = []
    with open("YandexRelPredChallenge.txt") as f:
        for line in f:
            words = line.split()
            sessionID_old = sessionID
            sessionID = int(words[0])
            if sessionID>sessionID_old:
                list_clicks.append(clicks)
                clicks = [0 for i in range(10)]
            recordType = words[2]
            if recordType=="Q":
                links = [int(l) for l in words[5:]]
            elif recordType=="C":
                link_clicked = int(words[3])
                if link_clicked in links:
                    rank_clicked = links.index(link_clicked)
                    clicks[rank_clicked] =1
    return(list_clicks)

def em():
    """
    TODO: check whether it is correct
    Expectation-maximization method for determining the parameters alpha and gamma, using training data.
    Using the update rules from: https://clickmodels.weebly.com/uploads/5/2/2/5/52257029/mc2015-clickmodels.pdf
    """
    # Use this: https://github.com/markovi/PyClick/blob/master/pyclick/utils/YandexRelPredChallengeParser.py to understand what is going on
    # https://www.kaggle.com/c/yandex-personalized-web-search-challenge#logs-format
    gamma = [0.5 for x in range(10)] #book
    alpha = 0.2 #book, initial probability clicked if not relevant
    tolerance = 0.01
    max_iter = 100
    click_log = yandex_log_parser()
    for i in range(max_iter):
        total = [1 for x in range(10)]
        for j in click_log:
            for rank in range(len(j)):
                gamma_value = gamma[rank]/total[rank]
                alpha_value = alpha/sum(total)
                if j[rank]==1:
                    gamma[rank] += 1
                    alpha += 1
                else:
                    alpha += (1-gamma_value)*alpha_value/(1-gamma_value*alpha_value)
                    gamma[rank] += (1-alpha_value)*gamma_value/(1-gamma_value*alpha_value)
                total[rank] += 1
        # New alpha and gamma
        alpha = alpha/sum(total)
        for x in range(len(gamma)):
            gamma[x] = gamma[x]/total[x]
    return (alpha,gamma)

(alpha,gamma) = em()

# It takes a ranked list l of relevance scores, and parameters alpha and gamma
# and outputs the probabilities that different elements are clicked in the end
def click_probabilities(l, alpha, gamma):
    return [abs(alpha - (1 - l[i]))*gamma[i] for i in range(3)]

# Takes a list of relevance scores and parameters, and returns for each position whether it is clicked or not
# 1 means a click.
def produce_clicks(list, alpha, gamma):
    probabilities = click_probabilities(list, alpha, gamma)    
    return [np.random.binomial(1, probabilities[i]) for i in range(3)]


# Based on a click-probability theta, clicks are completely random here.
def produce_clicks_random(list, theta):
    return [np.random.binomial(1, theta) for i in range(3)]


# Takes an interleaved list and a click pattern and returns the winner
def decide_winner(interl, clicks):
    clicks_E = 0
    clicks_P = 0
    for i in range(3):
        if (clicks[i] == 1):
            if (interl[i][1] == "E"):
                clicks_E += 1
            elif (interl[i][1] == "P"):
                clicks_P += 1
    if (clicks_E > clicks_P):
        return "E"
    elif (clicks_E < clicks_P):
        return "P"
    else:
        return "NW"

## Simulation of Interleaving Experiment

# This determines the win_proportion of a single pair, while we do the interleaving and click-experiment
# 500 times. (500 can be changed later)
# The second argument is the interleaving__method used (probabilistic or team_draft)
# The third argument specifies the function that determines the click_probabilities (position based or random)
def estimate_win_proportion(ranking_pair, interleaver, click_function, alpha, gamma, theta):
    k = 500
    wins_E = 0
    wins_P = 0
    for i in range(k):
        interl = interleaver(ranking_pair)
        relevance_list = get_relevance_list([elem[0] for elem in interl])
        if (click_function == produce_clicks):
            clicks = click_function(relevance_list, alpha, gamma)
        elif (click_function == produce_clicks_random):
            clicks = click_function(relevance_list, theta)
        winner = decide_winner(interl, clicks)
        if (winner == "E"):
            wins_E += 1
        elif (winner == "P"):
            wins_P += 1
            
    return wins_E / (wins_E + wins_P)

def compute_sample_size(p1):
    a = 0.05
    b = 0.1
    p0 = 0.5
    delta = abs(p1-p0)
    N_intermediate = ((norm.ppf(1 - a)*math.sqrt(p0*(1-p0)) + 
                      norm.ppf(1 - b)*math.sqrt(p1*(1 - p1)))
                      /delta)**2
    N = N_intermediate + 1/delta
    return N

def run_interleaving_experiment(deltaERRs, interleaver, click_function, alpha, gamma, theta):
    result = []
    counter = 0
    for i in range(len(deltaERRs)):
        if (len(deltaERRs[i])> 0):
            Ns = []
            for pair in deltaERRs[i]:
                p1 = estimate_win_proportion(pair, interleaver, click_function, alpha, gamma, theta)
                counter += 1
                print(counter)
                if (p1 != 0.5):
                    Ns += [compute_sample_size(p1)]
            minimum = min(Ns)
            maximum = max(Ns)
            median = statistics.median(Ns)
            result += [(minimum, median, maximum)]
    return result
