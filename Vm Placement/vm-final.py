import random
import numpy as np

# Function to take VM and PM input from user
def get_user_input():
    VMs = []
    PMs = []

    num_vms = int(input("Enter the number of Virtual Machines (VMs): "))
    for i in range(num_vms):
        cpu = int(input(f"Enter CPU requirement for VM{i+1}: "))
        VMs.append({"id": f"VM{i+1}", "cpu": cpu})

    num_pms = int(input("Enter the number of Physical Machines (PMs): "))
    for i in range(num_pms):
        cpu = int(input(f"Enter total CPU capacity for PM{i+1}: "))
        PMs.append({"id": f"PM{i+1}", "cpu": cpu})

    return VMs, PMs

# Get input from user
VMs, PMs = get_user_input()

P_idle = 162
P_busy = 215

# Parameters for Firefly Algorithm
alpha = 0.2  # Randomization factor
beta0 = 1.0  # Attractiveness
gamma = 1.0  # Absorption coefficient
num_fireflies = 20  # Firefly population
iterations = 50  # Number of iterations

num_VMs = len(VMs)
num_PMs = len(PMs)

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
    # Distribute VMs more evenly across PMs during initialization
    firefly = []
    pm_idx = 0
    for vm_idx in range(num_VMs):
        firefly.append(pm_idx)
        pm_idx = (pm_idx + 1) % num_PMs  # Rotate through available PMs
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
            # Reassign VM to another PM with available resources
            for new_pm_idx in range(num_PMs):
                if VMs[vm_idx]["cpu"] <= pm_resources[new_pm_idx]:
                    solution[vm_idx] = new_pm_idx
                    pm_resources[new_pm_idx] -= VMs[vm_idx]["cpu"]
                    break
        else:
            pm_resources[pm_idx] -= VMs[vm_idx]["cpu"]
    return solution

# Initialize population
fireflies = [generate_firefly() for _ in range(num_fireflies)]
costs = [power_consumption(f)[0] for f in fireflies]

best_solution = fireflies[np.argmin(costs)]
best_cost = min(costs)

# Run the Firefly Algorithm for a number of iterations
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

print("\nBest VM to PM Assignment:")
for vm_idx, pm_idx in enumerate(best_solution):
    print(f"  {VMs[vm_idx]['id']} -> {PMs[pm_idx]['id']}")

print("\nPower Consumption per PM:")
total, pm_power, pm_usage = power_consumption(best_solution)
for i in range(num_PMs):
    if pm_usage[i] > 0:
        utilization = pm_usage[i] / PMs[i]["cpu"] * 100
        print(f"  {PMs[i]['id']}: Utilized = {utilization:.1f}%, Power = {pm_power[i]:.2f}W")
    else:
        print(f"  {PMs[i]['id']}: Utilized = 0.0%, Power = 0.00W")

print("\nMinimum Total Power Consumption:", round(total, 3), "W")
