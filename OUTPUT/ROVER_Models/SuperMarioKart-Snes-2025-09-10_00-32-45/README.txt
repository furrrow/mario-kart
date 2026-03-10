This model, trained on 09-10-25, serves as the post-verification model in the ROVER paper.

Traces are located in model_08-27 and include the raw traces & post-processed traces (with acceleration and phidot).

episode_goodmario.mp4 is six Mario rollouts in one video.

The reward structure used to train this model is located in script.lua 

This model trained via ppo2 for 4 million timesteps on the stable-retro framework. Hyperparameters were unchanged from the original stable-retro-scripts/script/train.py file.

The Figure used in the photo is Figure1_after.png This photo was generated with plot_mario.py. The traces in this photo - unlike the one in the paper - was specifically ordered to display the red/violating traces on top. The figure in the paper displayed all traces in the random order that it was read into the plotting algorithm.

The results from telex are split into two files called:
- telex_results_mario_after_09-25
- telex_results_mario_after_02-26