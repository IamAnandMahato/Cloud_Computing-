# app.py
import streamlit as st

st.title("⚙️ Power-Aware VM Placement Simulator")

# Step 1: Input number of VMs and their CPU demands
num_vms = st.number_input("Enter number of Virtual Machines", min_value=1, step=1)
vm_cpu = []

for i in range(num_vms):
    cpu = st.number_input(f"Enter CPU demand of VM{i+1} (%)", min_value=1, max_value=100, step=1, key=f"vm_{i}")
    vm_cpu.append(cpu)

# Step 2: Input number of PMs and their CPU capacities
num_pms = st.number_input("Enter number of Physical Machines", min_value=1, step=1)
pm_capacity = []

for i in range(num_pms):
    cap = st.number_input(f"Enter CPU capacity of PM{i+1} (%)", min_value=1, max_value=1000, step=1, key=f"pm_{i}")
    pm_capacity.append(cap)

# Step 3: Run placement algorithm when button clicked
if st.button("🚀 Run Placement Algorithm"):
    P_idle = 162
    P_busy = 215
    power_diff = P_busy - P_idle

    pm_used = [0] * num_pms
    vm_allocation = [-1] * num_vms

    for i in range(num_vms):
        placed = False
        for j in range(num_pms):
            if pm_used[j] + vm_cpu[i] <= pm_capacity[j]:
                pm_used[j] += vm_cpu[i]
                vm_allocation[i] = j
                placed = True
                break
        if not placed:
            st.warning(f"❌ VM{i+1} could not be placed!")

    # Power Calculation
    total_power = 0
    st.subheader("🔌 Power Consumption per PM")
    for i in range(num_pms):
        if pm_used[i] > 0:
            utilization = pm_used[i] / pm_capacity[i]
            power = P_idle + (utilization * power_diff)
        else:
            utilization = 0
            power = 0
        st.write(f"PM{i+1}: Utilized = {utilization*100:.1f}%, Power = {power:.2f}W")
        total_power += power

    st.subheader("📦 VM Allocation")
    for i in range(num_vms):
        if vm_allocation[i] != -1:
            st.success(f"VM{i+1} → PM{vm_allocation[i]+1}")
        else:
            st.error(f"VM{i+1} → Not Placed ❌")

    st.markdown(f"### ⚡ Total Power Consumption: `{total_power:.2f} W`")
