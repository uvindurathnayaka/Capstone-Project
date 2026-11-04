import os
import glob
import torch
import gymnasium as gym
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig

if "SUMO_HOME" not in os.environ:
    os.environ["SUMO_HOME"] = "/usr/share/sumo"

def env_creator(env_config):
    import sumo_rl
    base_dir = os.path.dirname(os.path.abspath(__file__))
    net_path = os.path.abspath(os.path.join(base_dir, "..", "envs", "katubedda.net.xml"))
    route_path = os.path.abspath(os.path.join(base_dir, "..", "envs", "katubedda.rou.xml"))
    out_csv = os.path.abspath(os.path.join(base_dir, "..", "outputs", "katubedda_eval_metrics"))
    
    for f in glob.glob(out_csv + "*.csv"):
        try:
            os.remove(f)
        except OSError:
            pass

    return gym.make(
        "sumo-rl-v0",
        net_file=net_path,
        route_file=route_path,
        out_csv_name=out_csv,
        use_gui=True,      # GUI off for instant execution
        num_seconds=3600,    
        reward_fn="diff-waiting-time",
        delta_time=5,
        min_green=15
    )

if __name__ == "__main__":
    print("Initializing Ray for Katubedda AI Evaluation...")
    ray.init(ignore_reinit_error=True)
    register_env("katubedda_eval_env", env_creator)

    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=True,
            enable_env_runner_and_connector_v2=True,
        )
        .environment("katubedda_eval_env")
        .framework("torch")
        .env_runners(num_env_runners=0)
    )

    algo = config.build()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    checkpoint_dir = os.path.abspath(os.path.join(base_dir, "..", "outputs", "katubedda_checkpoint"))
    
    print(f"Loading trained weights from: {checkpoint_dir}")
    algo.restore(checkpoint_dir)

    print("Launching SUMO environment...")
    env = env_creator({})
    obs, info = env.reset()
    rl_module = algo.get_module("default_policy")

    done = False
    total_reward = 0.0
    step = 0

    while not done:
        if isinstance(obs, dict):
            obs_array = list(obs.values())[0]
        else:
            obs_array = obs

        obs_tensor = torch.tensor(obs_array, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            fwd_out = rl_module.forward_inference({"obs": obs_tensor})

        logits = fwd_out["action_dist_inputs"]
        action = torch.argmax(logits, dim=-1).item()

        obs, reward, terminated, truncated, info = env.step(action)
        
        if isinstance(reward, dict):
            total_reward += sum(reward.values())
        else:
            total_reward += reward

        if isinstance(terminated, dict):
            done = terminated.get("__all__", False) or truncated.get("__all__", False)
        else:
            done = terminated or truncated

        step += 1

    # FIX: Force sumo-rl to dump the metrics from RAM to disk!
    out_csv_path = os.path.abspath(os.path.join(base_dir, "..", "outputs", "katubedda_eval_metrics"))
    env.unwrapped.save_csv(out_csv_path, 1)

    print(f"\nEvaluation complete over {step} timesteps.")
    print(f"Cumulative Reward: {total_reward:.2f}")

    env.close()
    ray.shutdown()