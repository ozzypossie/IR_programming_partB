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
    Outputs the click-probability theta
    """
    rel_max = 1
    return (2**rel - 1)/2**rel_max

lst = [1, 1, 1]
print(compute_ERR(lst))
