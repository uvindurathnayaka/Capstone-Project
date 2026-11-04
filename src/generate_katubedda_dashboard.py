import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def get_latest_csv(prefix):
    # Absolute paths to safely locate the outputs directory
    search_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", f"{prefix}*.csv")
    files = glob.glob(search_path)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def generate_dashboard():
    base_csv = get_latest_csv("katubedda_baseline_metrics")
    eval_csv = get_latest_csv("katubedda_eval_metrics")
    
    if not base_csv or not eval_csv:
        print("❌ Error: Missing CSV files. Ensure baseline and evaluation scripts were run.")
        return
        
    df_base = pd.read_csv(base_csv)
    df_eval = pd.read_csv(eval_csv)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
    
    # -------------------------------------------------------------
    # 1. STATISTICAL SIGNIFICANCE TESTING
    # -------------------------------------------------------------
    wait_base = df_base['system_total_waiting_time']
    wait_ai = df_eval['system_total_waiting_time']
    
    # Welch's t-test (assumes unequal variance) and Mann-Whitney U (non-parametric)
    t_stat, p_val_t = stats.ttest_ind(wait_base, wait_ai, equal_var=False)
    u_stat, p_val_u = stats.mannwhitneyu(wait_base, wait_ai, alternative='two-sided')
    
    print("\n==================================================================")
    print("      STATISTICAL SIGNIFICANCE REPORT (ACADEMIC VERIFICATION)      ")
    print("==================================================================")
    print(f"Waiting Time Welch's t-test: t-statistic = {t_stat:.4f}, p-value = {p_val_t:.4e}")
    print(f"Waiting Time Mann-Whitney U: U-statistic = {u_stat:.4f}, p-value = {p_val_u:.4e}")
    
    if p_val_t < 0.001:
        print("RESULT: Statistically Significant Improvement (p < 0.001) - Null Hypothesis Rejected.")
    else:
        print("RESULT: Insufficient evidence of statistical significance.")
    print("==================================================================\n")

    # -------------------------------------------------------------
    # 2. GENERATE PUBLICATION-GRADE DASHBOARD
    # -------------------------------------------------------------
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle("Deep RL Traffic Controller (PPO) vs. Fixed-Time Baseline\nKatubedda Single-Junction Performance Profile", fontweight='bold', fontsize=16, y=0.98)

    c_base = '#d95f02' # Coral Red/Orange
    c_ai = '#1b9e77'   # Teak Green

    # Plot A: Cumulative Waiting Time
    axes[0, 0].plot(df_base['step'], df_base['system_total_waiting_time'].cumsum(), label='Fixed-Time Baseline', color=c_base, linewidth=2)
    axes[0, 0].plot(df_eval['step'], df_eval['system_total_waiting_time'].cumsum(), label='PPO Agent', color=c_ai, linewidth=2)
    axes[0, 0].set_title("A. Cumulative Network Delay Accumulation")
    axes[0, 0].set_xlabel("Simulation Step (seconds)")
    axes[0, 0].set_ylabel("Cumulative Delay (veh-sec)")
    axes[0, 0].legend(loc='upper left')

    # Plot B: Instantaneous Waiting Time Dynamics
    axes[0, 1].plot(df_base['step'], df_base['system_total_waiting_time'], label='Fixed-Time', color=c_base, alpha=0.7, linewidth=1.5)
    axes[0, 1].plot(df_eval['step'], df_eval['system_total_waiting_time'], label='PPO Agent', color=c_ai, alpha=0.9, linewidth=1.5)
    axes[0, 1].set_title("B. Real-Time System Waiting Time Dynamics")
    axes[0, 1].set_xlabel("Simulation Step (seconds)")
    axes[0, 1].set_ylabel("Waiting Time (s)")
    axes[0, 1].legend(loc='upper left')

    # Plot C: Queue Length Distribution Density
    sns.kdeplot(df_base['system_total_stopped'], ax=axes[1, 0], label='Fixed-Time', color=c_base, fill=True, alpha=0.3)
    sns.kdeplot(df_eval['system_total_stopped'], ax=axes[1, 0], label='PPO Agent', color=c_ai, fill=True, alpha=0.4)
    axes[1, 0].set_title("C. Queue Length Density Distribution")
    axes[1, 0].set_xlabel("Stopped Vehicles Count")
    axes[1, 0].set_ylabel("Probability Density")
    axes[1, 0].legend()

    # Plot D: Waiting Time Boxplot
    sns.boxplot(data=[df_base['system_total_waiting_time'], df_eval['system_total_waiting_time']], ax=axes[1, 1], palette=[c_base, c_ai])
    axes[1, 1].set_xticklabels(['Fixed-Time Baseline', 'PPO Agent'])
    axes[1, 1].set_title("D. System Waiting Time Variance & Outliers")
    axes[1, 1].set_ylabel("Waiting Time (s)")

    # Plot E: Percentile Tail Analysis
    percentiles = [50, 75, 90, 95, 99]
    base_p = np.percentile(df_base['system_total_waiting_time'], percentiles)
    eval_p = np.percentile(df_eval['system_total_waiting_time'], percentiles)
    x = np.arange(len(percentiles))
    width = 0.35
    axes[2, 0].bar(x - width/2, base_p, width, label='Fixed-Time', color=c_base)
    axes[2, 0].bar(x + width/2, eval_p, width, label='PPO Agent', color=c_ai)
    axes[2, 0].set_xticks(x)
    axes[2, 0].set_xticklabels([f'P{p}' for p in percentiles])
    axes[2, 0].set_title("E. Latency Tail Analysis (Percentile Profile)")
    axes[2, 0].set_ylabel("Waiting Time Threshold (s)")
    axes[2, 0].legend()

    # Plot F: Core KPI Overview
    metrics = ['Avg Wait', 'Max Wait', 'Avg Queue', 'Max Queue']
    base_m = [df_base['system_total_waiting_time'].mean(), df_base['system_total_waiting_time'].max(),
              df_base['system_total_stopped'].mean(), df_base['system_total_stopped'].max()]
    eval_m = [df_eval['system_total_waiting_time'].mean(), df_eval['system_total_waiting_time'].max(),
              df_eval['system_total_stopped'].mean(), df_eval['system_total_stopped'].max()]
    x_m = np.arange(len(metrics))
    axes[2, 1].bar(x_m - width/2, base_m, width, label='Fixed-Time', color=c_base)
    axes[2, 1].bar(x_m + width/2, eval_m, width, label='PPO Agent', color=c_ai)
    axes[2, 1].set_xticks(x_m)
    axes[2, 1].set_xticklabels(metrics, rotation=15)
    axes[2, 1].set_title("F. Core KPI Comparison Overview")
    axes[2, 1].set_ylabel("Metric Value")
    axes[2, 1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    dash_path = os.path.join(output_dir, "katubedda_evaluation_dashboard.png")
    plt.savefig(dash_path, dpi=300, bbox_inches='tight')
    print(f"📊 High-resolution analytics dashboard saved to: {dash_path}")
    plt.close()

if __name__ == "__main__":
    generate_dashboard()