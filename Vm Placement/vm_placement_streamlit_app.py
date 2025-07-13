
import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# Firefly parameters
P_idle = 162
P_busy = 215
alpha = 0.2
beta0 = 1.0
gamma = 1.0
num_fireflies = 20
iterations = 50

# Input interface
st.title("⚡ Power-aware VM Placement using Discrete Firefly Algorithm")

input_mode = st.radio("Select Input Mode", ["Auto-generate", "Manual"])

VMs, PMs = [], []

if input_mode == "Auto-generate":
    num_vms = st.number_input("Number of Virtual Machines (VMs)", 1, 100, 5)
    num_pms = st.number_input("Number of Physical Machines (PMs)", 1, 100, 3)
    if st.button("Generate Data"):
        for i in range(num_vms):
            cpu = random.randint(5, 20)
            VMs.append({"id": f"VM{i+1}", "cpu": cpu})

        for i in range(num_pms):
            cpu = random.randint(30, 60)
            PMs.append({"id": f"PM{i+1}", "cpu": cpu})

elif input_mode == "Manual":
    num_vms = st.number_input("Number of Virtual Machines (VMs)", 1, 100, 2)
    for i in range(num_vms):
        cpu = st.number_input(f"CPU for VM{i+1}", 1, 100, 10, key=f"vm{i}")
        VMs.append({"id": f"VM{i+1}", "cpu": cpu})

    num_pms = st.number_input("Number of Physical Machines (PMs)", 1, 100, 2)
    for i in range(num_pms):
        cpu = st.number_input(f"CPU for PM{i+1}", 1, 100, 50, key=f"pm{i}")
        PMs.append({"id": f"PM{i+1}", "cpu": cpu})

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
        if random.random() < beta0 * np.exp(-gamma * (f1[i] - f2[i]) ** 2):
            new_f[i] = f2[i]
        if random.random() < alpha:
            new_f[i] = random.randint(0, len(PMs) - 1)
    return repair_solution(new_f)

def repair_solution(solution):
    pm_resources = [pm["cpu"] for pm in PMs]
    for vm_idx, pm_idx in enumerate(solution):
        vm_cpu = VMs[vm_idx]["cpu"]
        if vm_cpu > pm_resources[pm_idx]:
            found = False
            for new_pm_idx in range(len(PMs)):
                if vm_cpu <= pm_resources[new_pm_idx]:
                    solution[vm_idx] = new_pm_idx
                    pm_resources[new_pm_idx] -= vm_cpu
                    found = True
                    break
        else:
            pm_resources[pm_idx] -= vm_cpu
    return solution

def optimize():
    fireflies = [generate_firefly() for _ in range(num_fireflies)]
    costs = [power_consumption(f)[0] for f in fireflies]

    best_solution = fireflies[np.argmin(costs)]
    best_cost = min(costs)

    for _ in range(iterations):
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
    return best_solution, best_cost

if st.button("Run DFA Optimization"):
    if not VMs or not PMs:
        st.warning("⚠️ Please provide VM and PM data first.")
    else:
        solution, total = optimize()
        total_power, pm_power, usage = power_consumption(solution)

        st.subheader("✅ Best VM to PM Assignment")
        for vm_idx, pm_idx in enumerate(solution):
            st.write(f"{VMs[vm_idx]['id']} → {PMs[pm_idx]['id']}")

        st.subheader("🔋 Power Consumption per PM")
        for i in range(len(PMs)):
            utilization = (usage[i] / PMs[i]["cpu"]) * 100 if PMs[i]["cpu"] != 0 else 0
            st.write(f"{PMs[i]['id']}: Utilization = {utilization:.1f}%, Power = {pm_power[i]:.2f} W")

        st.success(f"⚡ Minimum Total Power Consumption: {round(total_power, 2)} W")

        # Save CSV
        output_csv = "output_results.csv"
        with open(output_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["=== VM Details ==="])
            writer.writerow(["VM ID", "CPU"])
            for vm in VMs:
                writer.writerow([vm["id"], vm["cpu"]])
            writer.writerow([])

            writer.writerow(["=== PM Details ==="])
            writer.writerow(["PM ID", "CPU"])
            for pm in PMs:
                writer.writerow([pm["id"], pm["cpu"]])
            writer.writerow([])

            writer.writerow(["=== VM Assignment ==="])
            writer.writerow(["VM ID", "Assigned PM"])
            for vm_idx, pm_idx in enumerate(solution):
                writer.writerow([VMs[vm_idx]["id"], PMs[pm_idx]["id"]])
            writer.writerow([])

            writer.writerow(["=== PM Utilization and Power ==="])
            writer.writerow(["PM ID", "Utilization (%)", "Power (W)"])
            for i in range(len(PMs)):
                utilization = (usage[i] / PMs[i]["cpu"]) * 100 if PMs[i]["cpu"] != 0 else 0
                writer.writerow([PMs[i]["id"], f"{utilization:.1f}", f"{pm_power[i]:.2f}"])
            writer.writerow([])
            writer.writerow(["Total Power Consumption", round(total_power, 2)])

        st.download_button("📥 Download CSV", data=open(output_csv, "rb"), file_name=output_csv)

        # Save and show graph
        pm_ids = [pm["id"] for pm in PMs]
        utilization_percent = [(usage[i] / PMs[i]["cpu"]) * 100 if PMs[i]["cpu"] != 0 else 0 for i in range(len(PMs))]

        fig, ax1 = plt.subplots(figsize=(10, 6))
        bars = ax1.bar(pm_ids, utilization_percent, color='skyblue')
        ax1.set_ylabel('Utilization (%)', color='blue')
        ax1.set_ylim(0, 120)
        ax1.set_title('PM Utilization and Power Consumption (Optimized by DFA)')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(pm_ids, pm_power, color='red', marker='o', linewidth=2)
        ax2.set_ylabel('Power (W)', color='red')
        ax2.set_ylim(0, max(pm_power) + 50 if pm_power else 100)
        ax2.tick_params(axis='y', labelcolor='red')

        plt.tight_layout()
        plt.savefig("pm_utilization_graph.png")
        st.image("pm_utilization_graph.png", caption="PM Utilization vs Power", use_column_width=True)
        st.success("📊 Graph saved as: pm_utilization_graph.png")
