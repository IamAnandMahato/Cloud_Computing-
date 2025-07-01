# Power-Aware VM Placement with User Input

# Get user inputs
num_vms = int(input("Enter number of Virtual Machines: "))
vm_cpu = []
for i in range(num_vms):
    cpu = int(input(f"Enter CPU demand of VM{i+1} (in %): "))
    vm_cpu.append(cpu)

num_pms = int(input("\nEnter number of Physical Machines: "))
pm_capacity = []
for i in range(num_pms):
    cap = int(input(f"Enter CPU capacity of PM{i+1} (in %): "))
    pm_capacity.append(cap)

# Power consumption constants
P_idle = 162  # Idle power in watts
P_busy = 215  # Full usage power in watts
power_diff = P_busy - P_idle

# Initialize PM usage and VM allocation tracking
pm_used = [0] * num_pms
vm_allocation = [-1] * num_vms

# Allocate VMs to PMs (Greedy)
for i in range(num_vms):
    placed = False
    for j in range(num_pms):
        if pm_used[j] + vm_cpu[i] <= pm_capacity[j]:
            pm_used[j] += vm_cpu[i]
            vm_allocation[i] = j
            placed = True
            break
    if not placed:
        print(f"❌ VM{i+1} could not be placed!")

# Power Calculation
total_power = 0
print("\n--- Power Consumption per PM ---")
for i in range(num_pms):
    if pm_used[i] > 0:
        utilization = pm_used[i] / pm_capacity[i]
        power = P_idle + (utilization * power_diff)
    else:
        utilization = 0
        power = 0
    print(f"PM{i+1}: Utilized = {utilization*100:.1f}%, Power = {power:.2f}W")
    total_power += power

print("\n--- VM Allocation ---")
for i in range(num_vms):
    if vm_allocation[i] != -1:
        print(f"VM{i+1} → PM{vm_allocation[i]+1}")
    else:
        print(f"VM{i+1} → Not Placed ❌")

print(f"\n⚡ Total Power Consumption: {total_power:.2f}W")
