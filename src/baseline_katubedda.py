import os
import glob
import gymnasium as gym

if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = "/usr/share/sumo"

def run_katubedda_baseline():
    import sumo_rl

    base_dir = os.path.dirname(os.path.abspath(__file__))
    net_path = os.path.abspath(os.path.join(base_dir, "..", "envs", "katubedda.net.xml"))
    route_path = os.path.abspath(os.path.join(base_dir, "..", "envs", "katubedda.rou.xml"))
    out_csv = os.path.abspath(os.path.join(base_dir, "..", "outputs", "katubedda_baseline_metrics"))

    for f in glob.glob(out_csv + "*.csv"):
        try:
            os.remove(f)
        except OSError:
            pass

    env = gym.make(
        "sumo-rl-v0",
        net_file=net_path,
        route_file=route_path,
        out_csv_name=out_csv,
        use_gui=True,       
        num_seconds=3600,
        reward_fn="diff-waiting-time",
        delta_time=5
    )

    env.reset()
    done = False
    current_action = 0
    step_in_phase = 0
    total_steps = 0
    
    print("==========================================================")
    print("Starting Sri Lankan Time-of-Day (TOD) Baseline Simulation")
    print("Simulating Peak Hour dynamics (45s -> 90s -> 60s Green Extensions)")
    print("==========================================================")

    while not done:
        sim_time = total_steps * 5  # delta_time = 5 seconds
        
        # ---------------------------------------------------------
        # REAL-WORLD SRI LANKAN TOD SCHEDULE
        # ---------------------------------------------------------
        if sim_time < 1200:
            # First 20 mins: Ramping Up
            phase_0_steps = 9  # 45s Galle Rd
            phase_1_steps = 2  # 10s Southbound Turning
            phase_2_steps = 4  # 20s Campus Rd
        elif sim_time < 2700:
            # Next 25 mins: Extreme Peak Hour (Hold Galle Rd for 90s)
            phase_0_steps = 18 # 90s Galle Rd
            phase_1_steps = 3  # 15s Southbound Turning
            phase_2_steps = 6  # 30s Campus Rd
        else:
            # Last 15 mins: Ramping Down
            phase_0_steps = 12 # 60s Galle Rd
            phase_1_steps = 2  # 10s Southbound Turning
            phase_2_steps = 4  # 20s Campus Rd

        # ---------------------------------------------------------
        # CYCLE EXECUTION
        # ---------------------------------------------------------
        if current_action == 0 and step_in_phase >= phase_0_steps:
            current_action = 1
            step_in_phase = 0
        elif current_action == 1 and step_in_phase >= phase_1_steps:
            current_action = 2
            step_in_phase = 0
        elif current_action == 2 and step_in_phase >= phase_2_steps:
            current_action = 0
            step_in_phase = 0

        _, _, terminated, truncated, _ = env.step(current_action)
        
        if isinstance(terminated, dict):
            done = terminated.get("__all__", False) or truncated.get("__all__", False)
        else:
            done = terminated or truncated
            
        step_in_phase += 1
        total_steps += 1

    env.unwrapped.save_csv(out_csv, 1)
    env.close()
    print(f"Baseline simulation completed. Metrics saved successfully.")

if __name__ == "__main__":
    run_katubedda_baseline()