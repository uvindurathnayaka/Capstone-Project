## 1. Project Overview
This repository contains the Phase 1 implementation of an AI-driven traffic management system for the Katubedda intersection along the Galle Road corridor in Sri Lanka. The project utilizes Proximal Policy Optimization (PPO) via Ray RLlib to replace rigid Time-of-Day (TOD) signal controllers with a dynamic, state-responsive neural network.

## 2. Environment Architecture
The simulation environment is built using SUMO (Simulation of Urban MObility) and interfaced with Gymnasium via `sumo-rl`. 

### 2.1 Physical Network Constraints
* **Topology:** OpenStreetMap (OSM) extracted T-Junction (`cluster_1278003886_50422936`).
* **Demand Profiling:** Synthetic traffic generation scaled to 14-hour classified counts, strictly adhering to the JICA CoMTrans modal split (Cars 53.2%, 3-Wheelers 21.6%, Motorcycles 11.9%, Buses 9.1%, Trucks 4.2%).
* **Bus Priority Lane:** A dedicated physical bypass lane was implemented via Netedit, decoupling bus transit from the main traffic light phases to reflect real-world Sri Lankan infrastructure.

### 2.2 Reinforcement Learning Formulation
* **Observation Space:** High-resolution matrix containing vehicle density and queue lengths for all incoming arterial edges.
* **Action Space:** `Discrete(3)` representing target green phases:
  1. Action 0: Galle Road Dual Green (Northbound/Southbound)
  2. Action 1: Southbound-Only Phase 
  3. Action 2: Campus Road Minor Green
* **Reward Function:** Differential waiting time (`diff-waiting-time`). The agent is penalized for accumulating stationary vehicles and rewarded for discharging queues.
* * **Control Loop & Real-World Actuation:** The environment executes decisions at a 5-second `delta_time` to mirror the polling rates of standard traffic Programmable Logic Controllers (PLCs). A 15-second `min_green` parameter is enforced purely as an absolute safety floor (accounting for minimum pedestrian clearance and driver startup lost time). However, the PPO agent functions as a fully adaptive, volume-actuated controller: rather than cutting off at 15 seconds, the neural network dynamically extends the green phase (often holding it for 60–120+ seconds during extreme peak hours) to continuously flush heavy arterial platoons on Galle Road until the network reaches equilibrium.

## 3. Baseline Validation
To accurately measure AI performance, a highly realistic Time-of-Day (TOD) baseline was programmed. The baseline simulates professional Sri Lankan traffic engineering by adapting cycle lengths to peak demand:
* **0-20 min:** 45s Main Green
* **20-45 min (Peak):** 90s Main Green extension
* **45-60 min:** 60s Main Green

## 4. Evaluation & Results
The PPO agent was trained for 80 iterations using the New API Stack in Ray. The resulting policy was benchmarked against the dynamic TOD baseline over a 3,600-second evaluation episode.

**Key Dashboard Insights (See `katubedda_evaluation_dashboard.jpg`):**
* **Delay Suppression:** The cumulative network delay was reduced from >3.0M vehicle-seconds to ~0.5M vehicle-seconds.
* **Peak Latency Mitigation:** The fixed-time controller experienced cascading failure, with maximum wait times spiking above 10,000s. The PPO agent established an equilibrium, actively holding peak individual wait times to ~2,000s under identical loads.
* **Queue Density Optimization:** The queue length probability density shifted leftward, completely eliminating the $P_{99}$ long-tail outliers associated with arterial gridlock.

## 5. Next Steps (Phase 2)
With the single-junction mathematical foundation verified, the architecture will be scaled to a Multi-Agent Reinforcement Learning (MARL) framework covering the continuous Galle Road corridor up to Dehiwala.