# risk.py
def classify(score):
    """Classify risk level based on score."""
    if score < 3: return "🟢 LOW"
    elif score < 6: return "🟡 MEDIUM"
    else: return "🔴 HIGH"

def calculate_scores(inputs, weights):
    """Calculate likelihood, impact, severity, and weighted scores."""
    scores = [inputs[f]['value'] for f in inputs]
    weighted_scores = [scores[i]*weights[f] for i,f in enumerate(inputs)]
    
    likelihood = sum([inputs[f]['value']*weights[f] for f in list(inputs.keys())[:8]]) / sum([weights[f] for f in list(inputs.keys())[:8]])
    impact = sum([inputs[f]['value']*weights[f] for f in list(inputs.keys())[8:]]) / sum([weights[f] for f in list(inputs.keys())[8:]])
    severity = (likelihood + impact)/2
    return scores, weighted_scores, likelihood, impact, severity
