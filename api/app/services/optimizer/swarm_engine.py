import pulp

def optimize_load_shed(houses: dict, target_kw: float):
    prob = pulp.LpProblem("LoadShed", pulp.LpMinimize)
    shed_vars = {h: pulp.LpVariable(f"shed_{h}", 0, houses[h]["max_shed"]) for h in houses}
    prob += pulp.lpSum(shed_vars.values())
    total_load = sum(houses[h]["current_kw"] for h in houses)
    prob += total_load - pulp.lpSum(shed_vars.values()) <= target_kw
    prob.solve()
    return {h: shed_vars[h].value() for h in houses}

fake_neighborhood = {
    "house_1": {"current_kw": 5.2, "max_shed": 1.5},
    "house_2": {"current_kw": 3.8, "max_shed": 1.0},
    "house_3": {"current_kw": 6.1, "max_shed": 2.0},
}
print(optimize_load_shed(fake_neighborhood, target_kw=40))
