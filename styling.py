"""
This is an aviation crash simulator
"""
import random 
STATES = ['airport','air','crashed']

def mcmc(initial_state, transition_probabilities):
    """
    this functioon return a lists of aviation state arguments
    ----------
    i = string, representing a state
    transition_probability - dictionaries
    """
    state_list = [initial_state]        
    current_state = initial_state
    while current_state!='crashed':
        probs = transition_probabilities[current_state]
        current_state = random.choices(STATES, probs)[0]
        state_list.append(current_state)
        if state_list[-1] == 'crashed':
            return state_list

P = {'airport': [0.4, 0.6, 0.0],'air': [0.8, 0.19999, 0.00001],}
print(f"crashed after {len(mcmc('airport', P))} days of service")
