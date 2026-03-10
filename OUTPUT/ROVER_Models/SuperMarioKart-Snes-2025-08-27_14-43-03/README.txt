This model, trained on 08-27, serves as the pre-verification model in the ROVER paper.

Traces are located in model_08-27 and include the raw traces & post-processed traces (with acceleration and phidot).

episode.mp4 is a single Mario rollout video,

episode_badmario.mp4 and episode_badmario2.mp4 are six Mario rollouts in one video.

The reward structure used to train this model is located in script.lua 

This model trained via ppo2 for 3 million timesteps on the stable-retro framework. Hyperparameters were unchanged from the original stable-retro-scripts/script/train.py file.

The Figure used in the photo is Figure1_before.png This photo was generated with plot_mario.py. The traces in this photo - unlike the one in the paper - was specifically ordered to display the red/violating traces on top. The figure in the paper displayed all traces in the random order that it was read into the plotting algorithm.

The results from telex are split into two files called:
- telex_results_mario_before_09-25
- telex_results_mario_before_02-26