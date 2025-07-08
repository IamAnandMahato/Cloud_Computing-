import streamlit as st
import numpy as np
import random

st.title("VM to PM Allocation using Firefly Algorithm")

# Inputs for VMs
num_vms = st.number_input("Enter number of Virtual Machines (VMs):", min_value=1, step=1)
VMs = []

for i in range(num_vms):
    cpu = st.number_input(f"CPU requirement for VM{i+1}:", min_value=1, step=1, key=f"vm_{i}")
    VMs.append({"id": f"VM{i+1}", "cpu": cpu})

# Inputs for PMs
num_pms = st.number_input("Enter number of Physical Machines (PMs):", min_value=1, step=1)
PMs = []

for i in range(num_pms):
    cpu = st.number_input(f"CPU capacity for PM{i+1}:", min_value=1, step=1, key=f"pm_{i}")
    PMs.append({"id": f"PM{i+1}", "cpu": cpu})

# Parameters
P_idle = 162
P_busy = 215

alpha = 0.2
beta0 = 1.0
gamma = 1.0
num_fireflies = 20
iterations = 50

num_VMs = len(VMs)
num_PMs = len(PMs)

# Firefly functions
def power_consumption(assignments):
    usage = [0] * num_PMs
    pm_power = [0] * num_PMs

    for vm_idx, pm_idx in enumerate(assignments):
        usage[pm_idx] += VMs[vm_idx]["cpu"]

    total_power = 0
    for i, u in enumerate(usage):
        if u > 0:
            utilization = u / PMs[i]["cpu"] * 100
            power = P_idle + (P_busy - P_idle) * (utilization / 100)
            pm_power[i] = power
            total_power += power
        else:
            pm_power[i] = 0
    return total_power, pm_power, usage

def generate_firefly():
    firefly = []
    pm_idx = 0
    for vm_idx in range(num_VMs):
        firefly.append(pm_idx)
        pm_idx = (pm_idx + 1) % num_PMs
    return firefly

def distance(f1, f2):
    return np.sqrt(sum((i - j)**2 for i, j in zip(f1, f2)))

def move_firefly(f1, f2):
    new_f = f1[:]
    for i in range(num_VMs):
        if random.random() < beta0 * np.exp(-gamma * (f1[i] - f2[i])**2):
            new_f[i] = f2[i]
        if random.random() < alpha:
            new_f[i] = random.randint(0, num_PMs - 1)
    return repair_solution(new_f)

def repair_solution(solution):
    pm_resources = [PMs[i]["cpu"] for i in range(num_PMs)]
    for vm_idx, pm_idx in enumerate(solution):
        if VMs[vm_idx]["cpu"] > pm_resources[pm_idx]:
            for new_pm_idx in range(num_PMs):
                if VMs[vm_idx]["cpu"] <= pm_resources[new_pm_idx]:
                    solution[vm_idx] = new_pm_idx
                    pm_resources[new_pm_idx] -= VMs[vm_idx]["cpu"]
                    break
        else:
            pm_resources[pm_idx] -= VMs[vm_idx]["cpu"]
    return solution

if st.button("Run Firefly Algorithm"):
    if num_vms == 0 or num_pms == 0:
        st.warning("Please enter both VM and PM details.")
    else:
        fireflies = [generate_firefly() for _ in range(num_fireflies)]
        costs = [power_consumption(f)[0] for f in fireflies]

        best_solution = fireflies[np.argmin(costs)]
        best_cost = min(costs)

        for gen in range(iterations):
            for i in range(num_fireflies):
                for j in range(num_fireflies):
                    if costs[j] < costs[i]:
                        new_solution = move_firefly(fireflies[i], fireflies[j])
                        new_cost = power_consumption(new_solution)[0]
                        if new_cost < costs[i]:
                            fireflies[i] = new_solution
                            costs[i] = new_cost
                            if new_cost < best_cost:
                                best_solution = new_solution[:]
                                best_cost = new_cost

        st.subheader("Best VM to PM Assignment:")
        for vm_idx, pm_idx in enumerate(best_solution):
            st.write(f"{VMs[vm_idx]['id']} -> {PMs[pm_idx]['id']}")

        st.subheader("Power Consumption per PM:")
        total, pm_power, pm_usage = power_consumption(best_solution)
        for i in range(num_PMs):
            if pm_usage[i] > 0:
                utilization = pm_usage[i] / PMs[i]["cpu"] * 100
                st.write(f"{PMs[i]['id']}: Utilized = {utilization:.1f}%, Power = {pm_power[i]:.2f}W")
            else:
                st.write(f"{PMs[i]['id']}: Utilized = 0.0%, Power = 0.00W")

        st.success(f"Minimum Total Power Consumption: {round(total, 3)} W")
