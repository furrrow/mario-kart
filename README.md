# Qualifying Autonomous Systems: Learning from Mario Kart for Robust Safety

This repository contains code and resources for studying safety in autonomous systems using Stable-Retro's Mario Kart (SNES) and TurtleBot3's TurtleBot platform.

This repository serves as the **official repository** for the following works:

<a id="papers"></a>
1. **[A Framework for Black-Box Controller Design to Automatically Satisfy Specifications Using Signal Temporal Logic](https://ieeexplore.ieee.org/abstract/document/11007815)**, published at ICUAS 2025
2. **[ROVER: Regulator-Driven Robust Temporal Verification of Black-Box Robot Policies](https://arxiv.org/abs/2511.17781)**, pending publication.
3. **A Framework for Specification-Driven Design of Black-Box Controllers through Surrogate-Based Optimization**, pending publication.
4. **DRIVE-SAFE: Data-driven Robustness and Informed Validation
for Evolving Specifictions via Formal Evaluation**, pending publication.

### TODO:
- [ ] upload turtlebot weights to releases (which one should we upload?)
- [ ] add documentations on installing telex?
- [ ] add / confirm env_utils.py
- [ ] upload mariokart traces for DRIVE-SAFE
- [ ] add analysis python script for rtamt (including original rules)


# 🕹️ Simulation Engines
Two simulation engines are included: Mario Kart (SNES) and TurtleBot3. Although not all papers uses both simulators, this repository details the installation process for both engines.

Downloadable files are accessible in [our latest release](https://github.com/umd-xlab/mario-kart/releases/tag/v1.0.0).

## 🍄 MarioKart Install 

Following repos are needed for installing MarioKart:
- [Stable-Retro from Farama Foundations](https://github.com/Farama-Foundation/stable-retro)
- [Stable-Retro-Scripts from MatPoliquin](https://github.com/MatPoliquin/stable-retro-scripts)
- [Mario Kart SNES ROM files](https://github.com/esteveste/gym-SuperMarioKart-Snes)

We recommend creating git submodules such as:
```bash
git submodule add https://github.com/MatPoliquin/stable-retro-scripts
git submodule add https://github.com/esteveste/gym-SuperMarioKart-Snes
```

## 🚗 Training a mario-kart model
1. Move the specified `script.lua` to `mario-kart/stable-retro/retro/data/stable/SuperMarioKart-Snes`
2. Train the agent using `mario-kart/stable-retro-scripts/scripts/train.py` using either the modified `train.py` file provided in our repo, or the current `train.py` in the original stable-retro-scripts repo.
    1. `--num_timesteps` specifies the number of training timesteps. We recommend at least 1 million timesteps. More complex maps may require significantly more.
    2. `--num_env` specifies the number of parallel environments used during training. We recommend at least 4-8 environments.

> Pre-verification and post-verification models are available in our [latest release](https://github.com/umd-xlab/mario-kart/releases/tag/v1.0.0):
> - [pre-verification model](https://github.com/umd-xlab/mario-kart/releases/download/v1.0.0/preprocessed_traces_pre-verification_model.zip)
> - [post-verification model](https://github.com/umd-xlab/mario-kart/releases/download/v1.0.0/preprocessed_traces_post-verification_model.zip)

> **Note:** Due to uncertainties and randomness in the RL training process, results may not exactly replicate previously trained models. 
> 
## 🗺️ Generating traces from the mario-kart model
1. Confirm that training completed successfully. After training is finished, a new folder is created within `mario-kart/OUTPUT` titled `SuperMarioKart-Snes-[DATE]` and within it, a `.zip` file indicates that the model was trained successfully.
2. Run `python trace.py`. 
    1. `--num_traces` specifies the number of traces to generate. The default is 1.
    2. `--mode` specifies whether the simulation should be run in `series` or `parallel`. Parallel stacks videos into a 3x3 grid, so the recommended number of traces is 9 or fewer. Series generates one environment at a time and run faster. 

> **Note:** Pre-verification and post-verification model traces are stored within each model’s `model_[date]` folder. Traces used in our submission are provided in [our latest release](https://github.com/umd-xlab/mario-kart/releases/tag/v1.0.0).

## 🤖 Turtlebot3 Install

(This section is only needed for [ROVER](#papers)) Please closely follow the Turtlebot3 [e-manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/). 
The Turtlebot3 portion of this project is expected to be installed in a **separate ROS2 workspace**. 
The manual clones numerous repositories including their machine learning repo. Please follow the official documentations 
from the turtlebot3 repo except their Machine learning repo.

For this project, we have created a 
[fork of the Turtlebot3 Machine Learning repo](https://github.com/furrrow/turtlebot3_machine_learning/tree/custom). Please use 
our turtlebot3_machine_learning repo instead of theirs. All other repos should be cloned/installed from the turtlebot3 instructions.
- We have implemented a PPO agent instead of the original DQN agent.
- Please see [ppo_agent.py](https://github.com/furrrow/turtlebot3_machine_learning/blob/custom/turtlebot3_dqn/turtlebot3_dqn/ppo_agent.py) for further details.

After install, the project structure may look something like this:
```
~/turtlebot3_ws/
└─ src/
   └─ DynamixelSDK/
      turtlebot3/
      turtlebot3_msgs/
      turtlebot3_simulations/
      turtlebot3_machine_learning/ (clone our fork instead of the official repo)
      └─ turtlebot3_dqn/
         └─ saved_model/
            └─ stageXYZ.h5 (saved model files live here)
         └─ turtlebot3_dqn/
            └─ ppo_agent.py
               plot_h5_file.py
               ...
```

## Training a PPO model in TurtleBot3
We strongly encourage you to follow the official Turtlebot3 [machine-learning page](https://emanual.robotis.com/docs/en/platform/turtlebot3/machine_learning/#machine-learning).
After installation, please follow the documentation to make sure ROS2 is sourced, environment variables such as \$TURTLEBOT3_MODEL,
\$ROS_DOMAIN_ID are properly set. To run, four separate terminals are needed.
```bash
# Bring up the gazebo scenario
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage2.launch.py 
```
```bash
# Run Gazebo environment node
ros2 run turtlebot3_dqn dqn_gazebo 2
```
```bash
# Run DQN environment node
ros2 run turtlebot3_dqn dqn_environment
```
```bash
# launch the ppo_agent
python3 src/turtlebot3_machine_learning/turtlebot3_dqn/turtlebot3_dqn/ppo_agent.py
```

Our model weights are available in our [releases](https://github.com/umd-xlab/mario-kart/releases/tag/v1.0.0).
> Note, the turtlebot3 repo is constantly changing without notice. While we provide our model weights you may want to simply train new models from scratch.


## Generating traces from the TurtleBot3 model
Once PPO models are trained, they can be evaluated using a very similar process
```bash
# Bring up the gazebo scenario
ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage2.launch.py 
```
The dqn_gazebo.py will take an extra argument to save the goal location from the simulations
```bash
# Run Gazebo environment node & record goal locations
ros2 run turtlebot3_dqn dqn_gazebo 2 1
# the extra argument at the end triggers the node to record goal locations
```
```bash
# Run DQN environment node
ros2 run turtlebot3_dqn dqn_environment
```
the ppo_inference.py has a list of models that needs to be manually populated. The script will go through each model on the list,
evaluating them according to the number of episodes specified by the argparse argument.
```bash
# launch the ppo_agent using the inference script
python3 src/turtlebot3_machine_learning/turtlebot3_dqn/turtlebot3_dqn/ppo_inference.py --episodes 5
```
the above script will generate 2 files, a csv file with the goal locations during evaluation, and an h5 file 
containing the traces taken by the turtlebot. The traces and goals can be visualized using plot_h5_file.py (where the 
names of the h5 and csv files will need to be added manually),
or passed along to TeLEX for STL analysis.
# 🪛 Evaluation Methods
## 📐Calculating robustness with TeLEX
(This section is needed for [papers 1 2 \& 3](#papers))

[TeLEX](https://github.com/susmitjha/TeLEX) is a passive learning approach that infers STL formulas that characterize the behavior of a dynamical system using only observed signal traces of the system. TeLEX was used in a number of our publications (see Papers 1-3, above).

Follow the official installation instructions in the TeLEX repository. To run TeLEX on traces generated by this repository: 
1. Install TeLEX. Copy the `test_mario.py` or `test_turtlebots.py` file into the `tests/` directory. 
2. Copy the generated traces into the `data/` directory.  
3. Run in the Telex environment `python test_mario.py`. 

The output file reports the robustness score for each trace. Output TeLEX files used in our submission are provided in [our latest release](https://github.com/umd-xlab/mario-kart/releases/tag/v1.0.0).

## 📐 Calculating robustness with RTAMT
(This section is needed for [paper 4](#papers))

> 🚧 **This section is under construction.**

[RTAMT](https://github.com/nickovic/rtamt) is a python library for monitoring STLs. Compared to TeLEX, RTAMT is more recent, runs faster, and is easier to use.
While the RTAMT repository contains more support such as examples and a dockerfile, RTAMT can also be installed via Pip. 
RTAMT is already included in the project package requirements in pyproject.toml

A few examples of rtamt usage are included in [rtamt_mario/](./rtamt_mario) folder.


# ℹ️ Relevant Tips
A list of useful tips for working with the stable-retro framework. 

## 🎮 Inspecting Game Variables in Interactive Mode
1. In `mario-kart/stable-retro`, run `./gym-retro-integration`
2. In the Game drop-down menu, click **Load Game** navigate to your `SuperMarioKart-UMD` folder and select `rom.sha `.
3. The game will start from the beginning loading screen, but can also be loaded from a specific starting point in the game for RL Training, known as a **state**. To do the latter, in the Game drop-down menu, click **Load State** and navigate to the state you'd like to open within the `SuperMarioKart-UMD` folder. Look for a file with the suffix `.state`.
4. Various environmental parameters can be observed in the right-hand pane. It may also be useful to observe when the scenario is 'Done' for the ending condition. 

> Note: Tensorboard can be used to evaluate the training post-hoc. With a given training `.tfevents` data set, you can check the cumulative rewards / episode to ensure convergence. 

## 🆘 Relevant Documentation
Useful resources for the frameworks used in this project:

#### Reinforcement Learning
- [StableBaselines3 PPO documentation](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) 
- [OpenAI Spinning Up: PPO Explanation](https://spinningup.openai.com/en/latest/algorithms/ppo.html)

#### Environment Framework
- [Gymnasium Documentation](https://gymnasium.farama.org/) 
> Note: This project uses **Gym v0.21**, not Gymnasium v1.0+, so some APIs may differ. Refer to the migration guide if needed.

#### Emulator Framework
- [Stable-Retro documentation](https://stable-retro.farama.org/main/getting_started/) 
- [Stable-Retro Youtube Installation Video](https://www.youtube.com/watch?v=vPnJiUR21Og&t=423s&ab_channel=videogames.ai)

#### Community Support
- [Stable-Retro/Farama Foundations Discord]( https://discord.gg/dXuBSg3B4D)

#### Members
- [Kristy Sakano](https://kvsakano.github.io/), at kvsakano@umd.edu
- [Jim An](https://furrrow.github.io/), at jianyu34@umd.edu 
- [Alexis Chen](https://www.linkedin.com/in/alexischenn), undergraduate research assistant
- [Joe Mockler](https://www.linkedin.com/in/joe-mockler), at jmockle1@umd.edu
- [Dr. Mumu Xu](https://user.eng.umd.edu/~mumu/), at mumu@umd.edu


#### Citing
```
@INPROCEEDINGS{11007815,
  author={Sakano, Kristy and Mockler, Joe and Chen, Alexis and Xu, Huan},
  booktitle={2025 International Conference on Unmanned Aircraft Systems (ICUAS)}, 
  title={A Framework for Black-Box Controller Design to Automatically Satisfy Specifications Using Signal Temporal Logic}, 
  year={2025},
  volume={},
  number={},
  pages={587-594},
  keywords={Navigation;Closed box;Writing;Deep reinforcement learning;Logic;Aircraft;Optimization;Autonomous vehicles;Aerospace control},
  doi={10.1109/ICUAS65942.2025.11007815},
}

@misc{sakano2026roverregulatordrivenrobusttemporal,
      title={ROVER: Regulator-Driven Robust Temporal Verification of Black-Box Robot Policies}, 
      author={Kristy Sakano and Jianyu An and Dinesh Manocha and Huan Xu},
      year={2026},
      eprint={2511.17781},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2511.17781}, 
}

```
