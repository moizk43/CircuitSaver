import random

def stagger_restarts(shed_houses: list, window_minutes: int = 15):
    schedule = {}
    for house in shed_houses:
        delay = random.uniform(0, window_minutes)
        schedule[house] = delay
    return schedule
