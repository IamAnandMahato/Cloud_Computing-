
# 🚀 Adaptive Container Placement Simulator

This project simulates an **Adaptive Container Placement** strategy where user-defined containers (tasks) are assigned to Virtual Machines (VMs), calculating performance metrics such as **execution time**, **cost**, and **energy consumption**, and combines them into an **objective score**.

---

## 🧠 Features

- User inputs for:
  - Number of containers and VMs
  - Container workloads (in MI)
  - VM specifications (MIPS, cost, power)
- Manual container-to-VM allocation
- Calculates:
  - Execution time per VM
  - Cost per VM
  - Energy consumed per VM
  - Makespan, Total Cost, and Total Energy
  - Composite **Objective Score**
- Clean, console-based CLI interface

---

## 📸 Sample Demo

```bash
$ python main.py

--- Adaptive Container Placement ---
Enter number of containers: 2
Enter name of container 1: A
Enter length (in MI) of container A: 1000
Enter name of container 2: B
Enter length (in MI) of container B: 2000

Enter number of VMs: 2

--- Enter details for VM1 ---
MIPS: 500
Cost per second (₹): 0.2
Idle Power (W): 100
Max Power (W): 200

--- Enter details for VM2 ---
MIPS: 1000
Cost per second (₹): 0.3
Idle Power (W): 120
Max Power (W): 250

--- Container to VM Allocation ---
Assign container A to VM (1-2): 1
Assign container B to VM (1-2): 2
```

✅ **Sample Output**:
```
--- Results ---
VM Execution Times: {0: 2.0, 1: 2.0}
VM Costs: {0: 0.4, 1: 0.6}
VM Energies: {0: 300.0, 1: 370.0}

Makespan: 2.00 sec
Total Cost: ₹1.00
Total Energy: 670.00 Joules
Objective Score: 673.00
```

---

## 📦 Requirements

- Python 3.6 or higher
- No external libraries (uses standard Python collections)

---

## 🏁 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/adaptive-container-placement.git
   cd adaptive-container-placement
   ```

2. **Run the project**:
   ```bash
   python main.py
   ```

---

## 🔍 Objective Score Formula

The score is computed as:

```
Objective Score = α * Makespan + β * Total Cost + γ * Total Energy
```

Where α, β, and γ are equal weights (default: 1), but you can modify them in the code for different optimization strategies.

---

## ✅ Future Enhancements

- 🔄 Automated Optimal Allocation (via Greedy / Heuristic Search)
- 📊 Streamlit-based GUI for Visual Interaction
- 🧠 Integration with ML-based resource prediction
- ☁️ CloudSim-based simulation backend

---

## 👨‍💻 Author

**Anand Mahato**  
From: Dhanbad  
GitHub: [@IamAnandMahato](https://github.com/IamAnandMahato)

---

## 🪪 License

This project is open-source and available under the [MIT License](LICENSE).
