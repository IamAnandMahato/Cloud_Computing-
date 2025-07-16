import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# DFA Parameters
P_idle = 162
P_busy = 215
alpha = 0.2
beta0 = 1.0
gamma = 1.0
num_fireflies = 20
iterations = 50

st.set_page_config(page_title="🔥 VM Placement Optimizer", layout="centered")

st.title("🔥 Power-Aware VM Placement using Discrete Firefly Algorithm")

# Input Mode
mode = st.radio("Select Input Mode", ["Auto-generate", "Manual Input"])

VMs = []
PMs = []

# Inputs
if mode == "Auto-generate":
    num_vms = st.slider("Number of VMs", 1, 5000, 100)
    num_pms = st.slider("Number of PMs", 1, 3000, 100)
    for i in range(num_vms):
        VMs.append({"id": f"VM{i+1}", "cpu": random.randint(5, 20)})
    for i in range(num_pms):
        PMs.append({"id": f"PM{i+1}", "cpu": random.randint(30, 60)})
else:
    num_vms = st.number_input("Enter number of VMs", min_value=1, max_value=5000, step=1)
    num_pms = st.number_input("Enter number of PMs", min_value=1, max_value=3000, step=1)
    for i in range(int(num_vms)):
        cpu = st.number_input(f"CPU for VM{i+1}", min_value=1, step=1, key=f"vm{i}")
        VMs.append({"id": f"VM{i+1}", "cpu": cpu})
    for i in range(int(num_pms)):
        cpu = st.number_input(f"CPU for PM{i+1}", min_value=1, step=1, key=f"pm{i}")
        PMs.append({"id": f"PM{i+1}", "cpu": cpu})

# DFA Utility Functions
def power_consumption(assignments):
    usage = [0] * len(PMs)
    pm_power = [0] * len(PMs)
    for vm_idx, pm_idx in enumerate(assignments):
        usage[pm_idx] += VMs[vm_idx]["cpu"]
    total_power = 0
    for i, u in enumerate(usage):
        if u > 0:
            utilization = u / PMs[i]["cpu"]
            power = P_idle + (P_busy - P_idle) * utilization
            pm_power[i] = power
            total_power += power
        else:
            pm_power[i] = 0
    return total_power, pm_power, usage

def generate_firefly():
    firefly = []
    pm_idx = 0
    for vm_idx in range(len(VMs)):
        firefly.append(pm_idx)
        pm_idx = (pm_idx + 1) % len(PMs)
    return firefly

def move_firefly(f1, f2):
    new_f = f1[:]
    for i in range(len(VMs)):
        if random.random() < beta0 * np.exp(-gamma * (f1[i] - f2[i])**2):
            new_f[i] = f2[i]
        if random.random() < alpha:
            new_f[i] = random.randint(0, len(PMs) - 1)
    return repair_solution(new_f)

def repair_solution(solution):
    pm_resources = [PMs[i]["cpu"] for i in range(len(PMs))]
    for vm_idx, pm_idx in enumerate(solution):
        vm_cpu = VMs[vm_idx]["cpu"]
        if vm_cpu > pm_resources[pm_idx]:
            for new_pm_idx in range(len(PMs)):
                if vm_cpu <= pm_resources[new_pm_idx]:
                    solution[vm_idx] = new_pm_idx
                    pm_resources[new_pm_idx] -= vm_cpu
                    break
        else:
            pm_resources[pm_idx] -= vm_cpu
    return solution

# Run DFA
if st.button("Run DFA Optimization"):
    if not VMs or not PMs:
        st.error("❌ Please provide valid VM and PM data.")
    else:
        st.info("⏳ Optimization in progress... please wait.")
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

        total, pm_power, pm_usage = power_consumption(best_solution)

        st.success("✅ Optimization Complete")
        st.markdown(f"### ⚡ Total Power Consumption: **{round(total, 2)} W**")

        if num_vms <= 500:
            assignment_data = {
                "VM ID": [vm["id"] for vm in VMs],
                "Assigned PM": [PMs[pm_idx]["id"] for pm_idx in best_solution],
                "VM CPU": [vm["cpu"] for vm in VMs]
            }
            st.subheader("🧩 VM to PM Assignment")
            st.dataframe(pd.DataFrame(assignment_data))
        else:
            st.warning("📋 Assignment data too large to display! Please reduce VMs or export data to CSV.")

        if num_pms <= 500:
            utilization_data = {
                "PM ID": [pm["id"] for pm in PMs],
                "CPU Capacity": [pm["cpu"] for pm in PMs],
                "Used CPU": pm_usage,
                "Utilization (%)": [round((pm_usage[i] / PMs[i]["cpu"]) * 100, 1) for i in range(len(PMs))],
                "Power (W)": [round(p, 2) for p in pm_power]
            }
            st.subheader("📊 PM Utilization and Power")
            st.dataframe(pd.DataFrame(utilization_data))
        else:
            st.warning("📋 Utilization data too large to display! Please reduce PMs or export data to CSV.")

        if num_pms <= 300:
            st.subheader("📈 PM Utilization vs Power Graph")
            fig, ax1 = plt.subplots(figsize=(10, 5))
            pm_ids = [pm["id"] for pm in PMs]
            util_percent = [(pm_usage[i] / PMs[i]["cpu"]) * 100 if PMs[i]["cpu"] != 0 else 0 for i in range(len(PMs))]

            ax1.bar(pm_ids, util_percent, color='skyblue')
            ax1.set_ylabel('Utilization (%)', color='blue')
            ax1.set_ylim(0, 120)

            ax2 = ax1.twinx()
            ax2.plot(pm_ids, pm_power, color='red', marker='o')
            ax2.set_ylabel('Power (W)', color='red')
            ax2.set_ylim(0, max(pm_power) + 50)

            st.pyplot(fig)
        else:
            st.warning("📉 Too many PMs for graph! Graph limited to 300 PMs for clarity.")
