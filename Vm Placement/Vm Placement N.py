import numpy as np
import random

# -------------------------------
# Input Collection
# -------------------------------
def get_input_resources():
    num_pms = int(input("Enter number of PMs: "))
    pm_caps = []
    for i in range(num_pms):
        cpu = int(input(f"PM{i+1} CPU capacity: "))
        ram = int(input(f"PM{i+1} RAM capacity: "))
        pm_caps.append([cpu, ram])

    num_vms = int(input("\nEnter number of VMs: "))
    vm_reqs = []
    for i in range(num_vms):
        cpu = int(input(f"VM{i+1} CPU demand: "))
        ram = int(input(f"VM{i+1} RAM demand: "))
        vm_reqs.append([cpu, ram])

    return np.array(pm_caps), np.array(vm_reqs)

# -------------------------------
# Power Model
# -------------------------------
def power_consumption(cpu_used, ram_used, pm_cpu, pm_ram, pidle=162, pbusy=215):
    if cpu_used == 0 and ram_used == 0:
        return 0
    usage = max(cpu_used / pm_cpu, ram_used / pm_ram)
    return pidle + usage * (pbusy - pidle)

# -------------------------------
# Fitness: Total Power
# -------------------------------
def fitness(solution, vm_reqs, pm_caps):
    usage = np.zeros_like(pm_caps)
    for vm, pm in enumerate(solution):
        usage[pm] += vm_reqs[vm]

    total_power = 0
    for i in range(len(pm_caps)):
        total_power += power_consumption(usage[i][0], usage[i][1], pm_caps[i][0], pm_caps[i][1])
    return total_power

# -------------------------------
# Feasibility
# -------------------------------
def is_feasible(solution, vm_reqs, pm_caps):
    usage = np.zeros_like(pm_caps)
    for vm, pm in enumerate(solution):
        usage[pm] += vm_reqs[vm]
    return np.all(usage <= pm_caps)

# -------------------------------
# Firefly Movement
# -------------------------------
def hamming_distance(a, b):
    return np.sum(a != b)

def move_firefly(fi, fj, vm_reqs, pm_caps, beta0=1.0, gamma=1.0):
    new_fi = fi.copy()
    dist = hamming_distance(fi, fj)
    beta = beta0 * np.exp(-gamma * (dist ** 2))
    for i in range(len(fi)):
        if fi[i] != fj[i] and random.random() < beta:
            new_fi[i] = fj[i]

    # Mutation: change one VM's PM randomly (if it remains feasible)
    if random.random() < 0.1:
        idx = random.randint(0, len(fi) - 1)
        original = new_fi[idx]
        candidates = list(range(len(pm_caps)))
        random.shuffle(candidates)
        for pm in candidates:
            new_fi[idx] = pm
            if is_feasible(new_fi, vm_reqs, pm_caps):
                break
        else:
            new_fi[idx] = original

    if is_feasible(new_fi, vm_reqs, pm_caps):
        return new_fi
    else:
        return fi

# -------------------------------
# Initialize Fireflies
# -------------------------------
def initialize_population(n_fireflies, num_vms, num_pms, vm_reqs, pm_caps):
    population = []
    for _ in range(n_fireflies):
        while True:
            sol = np.random.randint(0, num_pms, size=num_vms)
            if is_feasible(sol, vm_reqs, pm_caps):
                break
        population.append(sol)
    return np.array(population)

# -------------------------------
# Main DFA Algorithm
# -------------------------------
def firefly_algorithm(vm_reqs, pm_caps, n_fireflies=30, max_gen=100):
    num_vms = len(vm_reqs)
    num_pms = len(pm_caps)

    fireflies = initialize_population(n_fireflies, num_vms, num_pms, vm_reqs, pm_caps)
    fits = np.array([fitness(f, vm_reqs, pm_caps) for f in fireflies])
    best = fireflies[np.argmin(fits)].copy()
    best_fit = min(fits)

    for gen in range(max_gen):
        for i in range(n_fireflies):
            for j in range(n_fireflies):
                if fits[j] < fits[i]:
                    new_sol = move_firefly(fireflies[i], fireflies[j], vm_reqs, pm_caps)
                    new_fit = fitness(new_sol, vm_reqs, pm_caps)
                    if new_fit < fits[i]:
                        fireflies[i] = new_sol
                        fits[i] = new_fit

        current_best = fireflies[np.argmin(fits)]
        current_fit = min(fits)
        if current_fit < best_fit:
            best = current_best.copy()
            best_fit = current_fit

    return best, best_fit

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    pm_caps, vm_reqs = get_input_resources()
    best_sol, best_power = firefly_algorithm(vm_reqs, pm_caps, n_fireflies=40, max_gen=200)

    print("\nFinal VM Placement:")
    pm_usage = np.zeros_like(pm_caps)
    pm_vms = [[] for _ in range(len(pm_caps))]

    for vm_idx, pm_idx in enumerate(best_sol):
        pm_usage[pm_idx] += vm_reqs[vm_idx]
        pm_vms[pm_idx].append(vm_idx + 1)

    for i, vms in enumerate(pm_vms):
        cpu, ram = pm_usage[i]
        power = power_consumption(cpu, ram, pm_caps[i][0], pm_caps[i][1])
        usage_percent = max(cpu / pm_caps[i][0], ram / pm_caps[i][1]) * 100
        if vms:
            print(f"  PM{i+1}: VMs {vms} - Usage: CPU={cpu}, RAM={ram} ({usage_percent:.1f}%) - Power = {power:.2f}W")
        else:
            print(f"  PM{i+1}: No VMs assigned - Power = 0.00W")

    print(f"\nTotal Power Consumption: {best_power:.2f}W")
