from collections import defaultdict

print("\n--- Adaptive Container Placement ---")

# === User Inputs ===
n = int(input("Enter number of containers: "))
containers = []
for i in range(n):
    name = input(f"Enter name of container {i+1}: ")
    length = float(input(f"Enter length (in MI) of container {name}: "))
    containers.append({"name": name, "length": length})

m = int(input("\nEnter number of VMs: "))
vms = []
for i in range(m):
    print(f"\n--- Enter details for VM{i+1} ---")
    mips = float(input("MIPS: "))
    cost = float(input("Cost per second (₹): "))
    p_idle = float(input("Idle Power (W): "))
    p_max = float(input("Max Power (W): "))
    vms.append({"id": i+1, "mips": mips, "cost_per_sec": cost, "p_idle": p_idle, "p_max": p_max})

print("\n--- Container to VM Allocation ---")
print("(Enter VM index starting from 1 for each container)")
allocation = []
for i, c in enumerate(containers):
    a = int(input(f"Assign container {c['name']} to VM (1-{m}): "))
    allocation.append(a)

# === Calculation ===
weights = {"alpha": 1, "beta": 1, "gamma": 1}
vm_exec_times = defaultdict(float)
vm_costs = defaultdict(float)
vm_energies = defaultdict(float)

for i, container in enumerate(containers):
    vm_id = allocation[i] - 1
    vm = vms[vm_id]

    exec_time = container["length"] / vm["mips"]
    vm_exec_times[vm_id] += exec_time
    vm_costs[vm_id] += exec_time * vm["cost_per_sec"]

makespan = max(vm_exec_times.values())

for vm_id, exec_time in vm_exec_times.items():
    vm = vms[vm_id]
    usage_ratio = exec_time / makespan
    power = vm["p_idle"] + (vm["p_max"] - vm["p_idle"]) * usage_ratio
    energy = power * makespan
    vm_energies[vm_id] = energy

total_cost = sum(vm_costs.values())
total_energy = sum(vm_energies.values())

# === Output ===
print("\n--- Results ---")
print("VM Execution Times:", dict(vm_exec_times))
print("VM Costs:", dict(vm_costs))
print("VM Energies:", dict(vm_energies))
print(f"\nMakespan: {makespan:.2f} sec")
print(f"Total Cost: ₹{total_cost:.2f}")
print(f"Total Energy: {total_energy:.2f} Joules")

obj_score = (
    weights["alpha"] * makespan +
    weights["beta"] * total_cost +
    weights["gamma"] * total_energy
)

print(f"Objective Score: {obj_score:.2f}")
