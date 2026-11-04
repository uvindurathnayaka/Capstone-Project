import os
import glob
import pandas as pd

def evaluate_performance():
    # Force absolute paths to locate the outputs folder accurately
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(current_dir, "..", "outputs"))
    
    print(f"Scanning for metrics in: {output_dir}")
    
    if not os.path.exists(output_dir):
        print(f"❌ Error: The directory {output_dir} does not exist.")
        return
        
    all_files = os.listdir(output_dir)
    print(f"Files currently in outputs folder: {all_files}\n")

    base_files = glob.glob(os.path.join(output_dir, "katubedda_baseline_metrics*.csv"))
    eval_files = glob.glob(os.path.join(output_dir, "katubedda_eval_metrics*.csv"))
    
    if not base_files or not eval_files:
        print("❌ Missing dataset! You must generate both CSVs for a valid comparison.")
        if not base_files:
            print(" -> Baseline CSV is missing. Run: python baseline_katubedda.py")
        if not eval_files:
            print(" -> Evaluation CSV is missing. Run: python evaluate_katubedda.py")
        return

    base_csv = max(base_files, key=os.path.getctime)
    eval_csv = max(eval_files, key=os.path.getctime)

    df_base = pd.read_csv(base_csv)
    df_eval = pd.read_csv(eval_csv)

    base_wait = df_base['system_total_waiting_time'].mean()
    eval_wait = df_eval['system_total_waiting_time'].mean()

    base_stopped = df_base['system_total_stopped'].mean()
    eval_stopped = df_eval['system_total_stopped'].mean()

    wait_diff = ((eval_wait - base_wait) / base_wait) * 100
    stopped_diff = ((eval_stopped - base_stopped) / base_stopped) * 100

    print("==========================================================")
    print(" KATUBEDDA JUNCTION PERFORMANCE BENCHMARK (A2 ARTERIAL)")
    print("==========================================================")
    print(f"Baseline Data:   {os.path.basename(base_csv)}")
    print(f"Trained AI Data: {os.path.basename(eval_csv)}")
    print("----------------------------------------------------------")
    print(f"1. Mean System Waiting Time:")
    print(f"   - Fixed-Time Baseline: {base_wait:.2f} s")
    print(f"   - PPO Agent:           {eval_wait:.2f} s")
    if wait_diff < 0:
        print(f"   -> 🏆 AI Reduced Waiting Time by {abs(wait_diff):.2f}%")
    else:
        print(f"   -> ❌ AI Increased Waiting Time by {wait_diff:.2f}%")

    print(f"\n2. Mean Stopped Queue Count:")
    print(f"   - Fixed-Time Baseline: {base_stopped:.2f} vehicles")
    print(f"   - PPO Agent:           {eval_stopped:.2f} vehicles")
    if stopped_diff < 0:
        print(f"   -> 🏆 AI Reduced Queue Count by {abs(stopped_diff):.2f}%")
    else:
        print(f"   -> ❌ AI Increased Queue Count by {stopped_diff:.2f}%")
    print("==========================================================\n")

if __name__ == "__main__":
    evaluate_performance()