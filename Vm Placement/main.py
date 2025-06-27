import streamlit as st
import numpy as np
import random

# --------------------------------
# Firefly Algorithm Functions (same as before)
# --------------------------------

def power_consumption(cpu_used, ram_used, pm_cpu, pm_ram, pidle=162, pbusy=215):
    if cpu_used == 0 and ram_used == 0:
        return 0
    usage = max(cpu_used / pm_cpu, ram_used / pm_ram)
    return pidle + usage * (pbusy - pidle)

def fitness(solution, vm_reqs, pm_caps):
    usage = np.zeros_like(pm_caps)
    for vm, pm in enumerate(solution):
        usage[pm] += vm_reqs[vm]
    total_power = 0
    for i in range(len(pm_caps)):
        total_power += power_consumption(usage[i][0], usage[i][1], pm_caps[i][0], pm_caps[i][1])
    return total_power

def is_feasible(solution, vm_reqs, pm_caps):
    usage = np.zeros_like(pm_caps)
    for vm, pm in enumerate(solution):
        usage[pm] += vm_reqs[vm]
    return np.all(usage <= pm_caps)

def hamming_distance(a, b):
    return np.sum(a != b)

def move_firefly(fi, fj, vm_reqs, pm_caps, beta0=1.0, gamma=1.0):
    new_fi = fi.copy()
    dist = hamming_distance(fi, fj)
    beta = beta0 * np.exp(-gamma * (dist ** 2))
    for i in range(len(fi)):
        if fi[i] != fj[i] and random.random() < beta:
            new_fi[i] = fj[i]
    if random.random() < 0.1:
        idx = random.randint(0, len(fi) - 1)
        original = new_fi[idx]
        for pm in random.sample(range(len(pm_caps)), len(pm_caps)):
            new_fi[idx] = pm
            if is_feasible(new_fi, vm_reqs, pm_caps):
                break
        else:
            new_fi[idx] = original
    return new_fi if is_feasible(new_fi, vm_reqs, pm_caps) else fi

def initialize_population(n_fireflies, num_vms, num_pms, vm_reqs, pm_caps):
    population = []
    for _ in range(n_fireflies):
        while True:
            sol = np.random.randint(0, num_pms, size=num_vms)
            if is_feasible(sol, vm_reqs, pm_caps):
                break
        population.append(sol)
    return np.array(population)

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

def run_firefly_algorithm(pm_caps, vm_reqs):
    best_sol, best_power = firefly_algorithm(vm_reqs, pm_caps, n_fireflies=40, max_gen=200)

    result = ""
    pm_usage = np.zeros_like(pm_caps)
    pm_vms = [[] for _ in range(len(pm_caps))]

    for vm_idx, pm_idx in enumerate(best_sol):
        pm_usage[pm_idx] += vm_reqs[vm_idx]
        pm_vms[pm_idx].append(vm_idx + 1)

    total_power = 0
    for i, vms in enumerate(pm_vms):
        cpu, ram = pm_usage[i]
        power = power_consumption(cpu, ram, pm_caps[i][0], pm_caps[i][1])
        usage_percent = max(cpu / pm_caps[i][0], ram / pm_caps[i][1]) * 100
        total_power += power
        if vms:
            result += f"PM{i+1}: VMs {vms} - CPU={cpu}, RAM={ram} ({usage_percent:.1f}%) - Power = {power:.2f}W\n"
        else:
            result += f"PM{i+1}: No VMs assigned - Power = 0.00W\n"

    total_vm_demand = np.sum(vm_reqs, axis=0)
    total_used_pm = np.sum(pm_usage, axis=0)
    total_pm_capacity = np.sum(pm_caps, axis=0)

    cpu_util = (total_used_pm[0] / total_pm_capacity[0]) * 100
    ram_util = (total_used_pm[1] / total_pm_capacity[1]) * 100

    result += "\nComparison Summary:\n"
    result += f"Total VM Demand:    CPU = {total_vm_demand[0]}, RAM = {total_vm_demand[1]}\n"
    result += f"Total PM Usage:     CPU = {total_used_pm[0]}, RAM = {total_used_pm[1]}\n"
    result += f"Total PM Capacity:  CPU = {total_pm_capacity[0]}, RAM = {total_pm_capacity[1]}\n"
    result += f"Utilization:        CPU = {cpu_util:.1f}%, RAM = {ram_util:.1f}%\n"
    result += f"Total Power:        {total_power:.2f}W\n"

    return result

# --------------------------------
# Streamlit App UI
# --------------------------------

st.title("🔥 VM Placement using Firefly Algorithm")

st.markdown("Enter PMs and VMs (one per line):")
col1, col2 = st.columns(2)

with col1:
    pm_text = st.text_area("PMs (CPU RAM)", value="100 100\n100 100")
with col2:
    vm_text = st.text_area("VMs (CPU RAM)", value="20 20\n40 40\n40 40\n40 50")

if st.button("Optimize Placement"):
    try:
        pm_lines = [list(map(int, line.strip().split())) for line in pm_text.strip().split('\n') if line.strip()]
        vm_lines = [list(map(int, line.strip().split())) for line in vm_text.strip().split('\n') if line.strip()]
        pm_caps = np.array(pm_lines)
        vm_reqs = np.array(vm_lines)

        result = run_firefly_algorithm(pm_caps, vm_reqs)

        st.success("✅ Optimization Complete")
        st.text_area("Result", result, height=400)

    except Exception as e:
        st.error(f"Error: {e}")
