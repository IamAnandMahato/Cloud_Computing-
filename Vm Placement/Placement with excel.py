# app.py
import streamlit as st
import pandas as pd
import io

st.title("⚙️ Power-Aware VM Placement Simulator")

# Upload Excel file
uploaded_file = st.file_uploader("📤 Upload Excel file (optional)", type=["xlsx"])

# Initialize data lists
vm_cpu, pm_capacity = [], []

# If file is uploaded, read from Excel
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=None)
    try:
        vm_cpu = df['VMs']['CPU (%)'].tolist()
        pm_capacity = df['PMs']['CPU Capacity (%)'].tolist()
        st.success("✅ Excel data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
else:
    # Step 1: Manual VM Input
    num_vms = st.number_input("Enter number of Virtual Machines", min_value=1, step=1)
    for i in range(num_vms):
        cpu = st.number_input(f"Enter CPU demand of VM{i+1} (%)", min_value=1, max_value=100, step=1, key=f"vm_{i}")
        vm_cpu.append(cpu)

    # Step 2: Manual PM Input
    num_pms = st.number_input("Enter number of Physical Machines", min_value=1, step=1)
    for i in range(num_pms):
        cap = st.number_input(f"Enter CPU capacity of PM{i+1} (%)", min_value=1, max_value=1000, step=1, key=f"pm_{i}")
        pm_capacity.append(cap)

# Step 3: Run Placement Algorithm
if st.button("🚀 Run Placement Algorithm"):
    if not vm_cpu or not pm_capacity:
        st.error("❗ Please provide valid VM and PM data.")
    else:
        num_vms = len(vm_cpu)
        num_pms = len(pm_capacity)
        P_idle = 162
        P_busy = 215
        power_diff = P_busy - P_idle

        pm_used = [0] * num_pms
        vm_allocation = [-1] * num_vms
        results = []

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
        power_data = []
        for i in range(num_pms):
            if pm_used[i] > 0:
                utilization = pm_used[i] / pm_capacity[i]
                power = P_idle + (utilization * power_diff)
            else:
                utilization = 0
                power = 0
            power_data.append({
                'PM': f"PM{i+1}",
                'Utilization (%)': round(utilization * 100, 1),
                'Power (W)': round(power, 2)
            })
            st.write(f"PM{i+1}: Utilized = {utilization*100:.1f}%, Power = {power:.2f}W")
            total_power += power

        st.subheader("📦 VM Allocation")
        for i in range(num_vms):
            if vm_allocation[i] != -1:
                st.success(f"VM{i+1} → PM{vm_allocation[i]+1}")
                results.append({'VM': f'VM{i+1}', 'Allocated PM': f'PM{vm_allocation[i]+1}'})
            else:
                st.error(f"VM{i+1} → Not Placed ❌")
                results.append({'VM': f'VM{i+1}', 'Allocated PM': 'Not Placed'})

        st.markdown(f"### ⚡ Total Power Consumption: `{total_power:.2f} W`")

        # Prepare result Excel
        result_df = pd.DataFrame(results)
        power_df = pd.DataFrame(power_data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, sheet_name='VM Allocation', index=False)
            power_df.to_excel(writer, sheet_name='Power Consumption', index=False)
            summary_df = pd.DataFrame([{'Total Power Consumption (W)': round(total_power, 2)}])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        st.download_button(
            label="📥 Download Result Excel",
            data=output.getvalue(),
            file_name="vm_placement_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )