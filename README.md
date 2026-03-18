# Qualifying Autonomous Systems: Learning from Mario Kart for Robust Safety

## Members
- Kristy Sakano, at kvsakano@umd.edu
- Alexis Chen undergraduate research assistant
- Joe Mockler (September 2024 - October 2025)
- Dr. Mumu Xu, at mumu@umd.edu


## How to Install

Necessary software include:
- [Stable-Retro from Farama Foundations](https://github.com/Farama-Foundation/stable-retro)
- [Stable-Retro-Scripts from MatPoliquin](https://github.com/MatPoliquin/stable-retro-scripts)
- Mario Kart SNES ROM files

[This youtube video](https://www.youtube.com/watch?v=vPnJiUR21Og&t=423s&ab_channel=videogames.ai) created by Matt is very helpful for installing Stable Retro.

Reach out to one of the developers if you have any questions.

## Relevant Code

### Examine the game in interactive mode to find relevant environmental parameters
1. In `mario-kart/stable-retro`, run `./gym-retro-integration`
2. In the Game drop-down menu, click **Load Game** navigate to your `SuperMarioKart-UMD` folder and select `rom.sha `.
3. The game will start from the beginning loading screen, but can also be loaded from a specific starting point in the game for RL Training, known as a **state**. To do the latter, in the Game drop-down menu, click **Load State** and navigate to the state you'd like to open within the `SuperMarioKart-UMD` folder. Look for a file with the suffix `.state`.
4. Various environmental parameters can be observed in the right-hand pane. It may also be useful to observe when the scenario is 'Done' for the ending condition. 

### Train the RL agent
1. Ensure that your reward structure in `mario-kart/stable-retro/retro/data/stable/SuperMarioKart-UMD/script.lua` is appropirate for the scenario you are trying to run.
2. Ensure that you have the right parameters set up for your model to start training in `mario-kart/stable-retro-scripts/scripts/train.py`.
3. Train your agent from the `mario-kart/stable-retro-scripts/scripts` directory. Run `python3 train.py`
    1. `--num_timesteps` specifies how many timesteps your model will train for. We recommend at least 1 million timesteps. A higher number of timesteps is necessary for a more complicated map.
    2. `--num_env` specifies how many environments will be spawned simultaneously. We recommend using between 4-8 agents and at least 1 million timesteps. A higher number of timesteps is necessary for training longer sections of the map.

### Test the agent & generate traces
1. Ensure that the model was trained to completion. After training is finished, a new folder is created within `mario-kart/OUTPUT` titled `SuperMarioKart-Snes-[DATE]` and within it, a `.zip` file indicates that the model was trained successfully.
2. Test the model with `python trace.py`. 
    1. `--num_traces` specifies how many traces will be generated; 1 is the default.
    2. `--mode` specifies whether the simulation should be run in `series` or `parallel`. Parallel will stack videos into a 3x3 grid, so the recommended number of traces is 9 or fewer. Series will generate one environment at a time and run faster. 
4. Git add, commit, and push to Github with commentary, if applicable.

### Training Evaluation with Tensorboard
We're using Tensorboard to evaluate the training post-hoc. With a given training .tfevents data set, you can check the cumulative rewards / episode to ensure convergence. To install and run...
1. Install tensorflow (contains tensorboard) if not already done. `pip install tensorflow`
2. Put the .tfevents file in an accessible folder with NO spaces in the file path
3. Open your python (or cmd) terminal and run `tensorboard.main --logdir`
4. Then open `http://localhost:6006/` (or whatever localhost is recommended by tensorboard) in your browser. This should be the board to inspect data!


## Relevant Documentation

1. [StableBaselines3 PPO webpage](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html) details the PPO algorithm we are using within our RL agent. They have example links to other websites and examples that are worth checking out.
    1. [OpenAI also has a blog on PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html) which is pretty handy. 
2. [Gymnasium Documentation](https://gymnasium.farama.org/) is the interface we are using. It was originally called Gym and maintained by OpenAI, but they semi-retired the project and Farama Foundation picked it up to provide long-term support and maintenance. It's important to note that we are still using v0.21 and not v1.0.0 so some of the documentation might be slightly different, so if you notice anything strange, check out their Migration Guide.
    1. You can also read OpenAI's gym documentation, but it is out-of-date and the website recommends reading the Gymnasium documentation instead.
3. [Stable-Retro documentation](https://stable-retro.farama.org/main/getting_started/) is also very useful. Gymnasium hosts a bunch of different software but this one is the one we're using; it emulates older video games & let's us train them with RL.


