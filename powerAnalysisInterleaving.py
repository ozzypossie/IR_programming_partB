from itertools import permutations

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
        deltaERR = compute_ERR(i[0]) - compute_ERR([1])
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
def td_interleave():
    """
    TODO
    Returns an interleaved list using Team-Draft Interleaving.
    """
    return []

def pr_interleave():
    """
    TODO
    Returns an interleaved list using Probabilistic Interleaving.
    """
    return []

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

def click_probabilities():
    """
    TODO
    Returns a list of click-probabilities for each document in a ranking list.
    """
    return []

def produce_clicks(list):
    """
    TODO
    Outputs a list of clicks for a list (1 is click, 0 is no click).
    """
    probabilities = click_probabilities(list)
    return []

def produce_clicks_random(list):
    """
    TODO
    Outputs a list of clicks using a Random Click Model.
    """

def decide_winner(list):
    """
    TODO
    Takes as input a pair of ranking lists. E.g. of the form [(doc_id1,"E"),(doc_id2,"P"),(doc_id3,"E")].
    """
    produce_clicks(list)
    return []

## Simulation of Interleaving Experiment

def estimate_win_proportion(ranking_pair):
    """
    TODO
    Runs interleaving experiment k times for each pair in ranking_pairs.
    """
    k = 500
    proportion = 0
    for i in range(k):
        # interleave
        # click simulation
        print("Please implement me first!")
    return compute_sample_size(proportion)

def compute_sample_size(p1):
    """
    TODO
    Computes the sample size with as input a proportion.
    """
    alpha = 0.05
    beta = 0.1
    p0 = 0.5
    delta = abs(p1-p0)
    return 0

def run_interleaving_experiment(ranking_pairs):
    """
    TODO
    Runs the interleaving experiment for each ranking pair in ranking_pairs.
    This function puts the estimated samples sizes in the right binself.
    Returns a list for each bin a tuple (min,median,max).
    """
    return []
