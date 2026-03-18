"""
Play a model with SuperMarioKart-Snes
"""

import warnings
warnings.filterwarnings("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
import glob
import csv
import random
import numpy as np
import tkinter as tk
from tkinter import filedialog
import torch
import imageio

import retro
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecFrameStack, VecTransposeImage
from env_utils import make_retro
from stable_baselines3.common.atari_wrappers import ClipRewardEnv, WarpFrame

def find_zip_in_folder(folder_path):
    zip_files = glob.glob(os.path.join(folder_path, "*.zip"))
    if not zip_files:
        raise FileNotFoundError(f"No .zip files found in {folder_path}")
    return zip_files[0]

def find_latest_model(base_dir="../../OUTPUT"):
    folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir)
               if os.path.isdir(os.path.join(base_dir, d))]
    if not folders:
        raise FileNotFoundError("No folders found in OUTPUT directory.")
    folders.sort(key=os.path.getmtime)
    latest_folder = folders[-1]
    model_zip = find_zip_in_folder(latest_folder)
    model_path = os.path.join(latest_folder, model_zip)
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found.")
    return model_path

def pick_model_folder(base_dir="../../OUTPUT"):
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(initialdir=base_dir, title="Select Model Folder")
    root.destroy()
    if not folder_selected:
        raise ValueError("No folder selected.")
    return folder_selected

def make_env(rank, base_seed=0):
    def _init():
        env = make_retro(game=args.game, state=args.state, scenario=args.scenario, num_players=1)
        env.action_space.seed(base_seed+rank)
        env = WarpFrame(env)
        env = ClipRewardEnv(env)
        return env
    return _init

def create_envs(num_envs, base_seed):
    return SubprocVecEnv([make_env(i, base_seed) for i in range(num_envs)])

def run_single_trace(env, model, trace_seed, output_dir, trace_idx):
    random.seed(trace_seed)
    np.random.seed(trace_seed)
    torch.manual_seed(trace_seed)

    obs = env.reset()
    done = [False]
    total_reward = 0
    step = 0

    frames_dir = os.path.join(output_dir, f"frames")
    os.makedirs(frames_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"playback_trace{trace_idx:02d}.csv")

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["step","kart1_X","kart1_Y","kart1_direction","kart1_speed",
                         "DrivingMode","GameMode","getFrame","current_checkpoint",
                         "surface","lap","reward","total_reward"])

        while not done[0]:
            frame = env.render(mode='rgb_array')#[0]
            imageio.imwrite(os.path.join(frames_dir, f"frame_{step:04d}.png"), frame)
            
            if (trace_idx == args.num_traces - 1):
                env.render(mode='human')
            if trace_idx == 0:
                action, _ = model.predict(obs, deterministic=True)
            else:
                action, _ = model.predict(obs, deterministic=False)

            obs, rewards, done, infos = env.step(action)
            total_reward += rewards[0]

            info = infos[0]
            data = [step,
                    info.get("kart1_X",0), info.get("kart1_Y",0), info.get("kart1_direction",0),
                    info.get("kart1_speed",0), info.get("DrivingMode",0), info.get("GameMode",0),
                    info.get("getFrame",0), info.get("current_checkpoint",0), info.get("surface",0),
                    info.get("lap",0), rewards[0], total_reward]
            writer.writerow(data)
            step += 1

def run_parallel_traces(env, model, num_traces, output_dir):
    obs = env.reset()
    done = [False]*num_traces
    total_reward = [0]*num_traces
    step = 0

    frames_dir = os.path.join(output_dir, "frames_parallel")
    os.makedirs(frames_dir, exist_ok=True)


    while not all(done):
        frame = env.render(mode='rgb_array')
        imageio.imwrite(os.path.join(frames_dir, f"frame_{step:05d}.png"),frame)

        action, _ = model.predict(obs, deterministic=False)
        obs, rewards, done, infos = env.step(action)
        env.render(mode='human')

        step += 1


def main():
    import argparse
    global args
    parser = argparse.ArgumentParser(description="Play model with trace logging")
    parser.add_argument("--model", default='pick', help="Path to trained model")
    parser.add_argument("--game", default="SuperMarioKart-Snes")
    parser.add_argument("--state", default=retro.State.DEFAULT)
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--num_traces", default=1, type=int)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--mode", choices=['series','parallel'], default='series',
                        help="Run traces sequentially ('series') or simultaneously ('parallel')")
    args = parser.parse_args()

    if args.model == "pick": #the default
        folder = pick_model_folder()
        print(f"[INFO] Selected folder: {folder}")
        args.model = find_zip_in_folder(folder)
        output_dir = os.path.dirname(args.model)
    elif args.model == "latest":
        args.model = find_latest_model()
        print(f"[INFO] Using latest model: {args.model}")
        output_dir = os.path.dirname(args.model)
    else:
        output_dir = os.path.dirname(args.model)

    if args.mode == 'series': # the default
        env = create_envs(1, args.seed)
        env = VecTransposeImage(VecFrameStack(env, n_stack=4))
        model = PPO.load(args.model, env=env)
        for i in range(args.num_traces):
            run_single_trace(env, model, args.seed+i, output_dir, i)
    elif args.mode == 'parallel':
        env = create_envs(args.num_traces, args.seed)
        env = VecTransposeImage(VecFrameStack(env, n_stack=4))
        model = PPO.load(args.model, env=env)
        run_parallel_traces(env, model, args.num_traces, output_dir)

if __name__ == "__main__":
    main()
