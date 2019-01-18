### OFFLINE EVALUATION

def compute_ERR(list):
    """
    Outputs the ERR measure of the rankinglist ([rel1, rel2, rel3]).
    """
    ERR = 0
    for r in range(len(list)):
        theta_r = compute_click_probability(list[r])
        prod = 1
        for i in range(r):
            prod *= (1-compute_click_probability(list[i]))
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
    TODO
    Outputs a list of tuples with all possible ranking pairs from a pool of 12 document ids.
    """

    return [([],[])]

def get_relevance(doc):
    """
    Outputs the relevance of the document, given as integer.
    """
    if (doc<0 or doc>12):
        raise Exception('Document id should be from 0 to 12!')

    if doc<6:
        return 0
    else:
        return 1

def divide_pairs_over_bins(list_pairs):
    """
    Dividines a list of pairs over 10 bins according to the delta ERR.
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

pairs = [] #list of all distinct ranking pairs
deltaERRs = []
lst = [1, 1, 1]
print(compute_ERR(lst))

print(divide_pairs_over_bins([([1,1,0],[0,0,1]),([1,0,1],[0,0,0])]))

### ONLINE EVALUATION
