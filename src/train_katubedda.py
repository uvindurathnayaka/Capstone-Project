import os
import shutil
import ray
import gymnasium as gym
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig

if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = "/usr/share/sumo"

def env_creator(env_config):
    import sumo_rl
    
    net_path = os.path.join(os.path.dirname(__file__), "..", "envs", "katubedda.net.xml")
    route_path = os.path.join(os.path.dirname(__file__), "..", "envs", "katubedda.rou.xml")
    out_csv = os.path.join(os.path.dirname(__file__), "..", "outputs", "katubedda_train_metrics")
    
    # EXACT match to the working baseline. No invalid arguments.
    return gym.make(
        "sumo-rl-v0",
        net_file=net_path,
        route_file=route_path,
        out_csv_name=out_csv,
        use_gui=False,       
        num_seconds=3600,    
        reward_fn="diff-waiting-time",
        min_green=15
    )

if __name__ == "__main__":
    print("Initializing Ray for Katubedda RL Agent...")
    ray.init(ignore_reinit_error=True)
    
    register_env("katubedda_env", env_creator)

    print("Configuring PPO Neural Network...")
    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=True,
            enable_env_runner_and_connector_v2=True,
        )
        .environment("katubedda_env")
        .env_runners(
            num_env_runners=0,    # <--- FIX: Forces local execution so errors are never hidden
            sample_timeout_s=600  
        )
        .framework("torch")
        .training(
            gamma=0.99, 
            lr=1e-4,
            train_batch_size=3600
        )
    )

    algo = config.build()
    
    best_reward = float('-inf')
    checkpoint_dir = os.path.join(os.path.dirname(__file__), "..", "outputs", "katubedda_checkpoint")

    print("\n==========================================================")
    print("Starting AI Training Loop for Katubedda Junction")
    print("Algorithm: PPO (Proximal Policy Optimization)")
    print("Target Iterations: 30")
    print("==========================================================")
    
    for i in range(80):
        result = algo.train()
        
        env_stats = result.get("env_runners", {})
        mean_reward = env_stats.get("episode_return_mean", env_stats.get("episode_reward_mean", -9999))
        episodes_done = env_stats.get("episodes_this_iter", 0)
        
        print(f"Iteration {i+1:02d} | Mean Reward: {mean_reward:.2f} | Episodes Finished: {episodes_done}")

        if mean_reward > best_reward and mean_reward != -9999:
            best_reward = mean_reward
            print(f"  -> AI Improved! Saving new best model...")
            
            if os.path.exists(checkpoint_dir):
                shutil.rmtree(checkpoint_dir)
            algo.save(checkpoint_dir)
        
    print("\n==========================================================")
    if best_reward != float('-inf'):
        print(f"Training complete! Best Cumulative Reward: {best_reward:.2f}")
        print(f"Model checkpoint saved to: {checkpoint_dir}")
    else:
        print("Training failed to produce a valid model.")
    print("==========================================================")
    
    ray.shutdown()