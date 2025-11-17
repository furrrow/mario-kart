# Plot Mario driving on track

# start pos is (3712, 2288)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import tkinter as tk          # Package for UI selection of folders
from tkinter import filedialog
import os
import glob # For wildcard selection

# Load the track map
#map_img = mpimg.imread("Racetrack_map_withgreen - Copy.png")
map_img = mpimg.imread("koopabeach_modified_dynamic.png")

# Load Mario's trace
root = tk.Tk()
root.withdraw()  # Hide the main window
folder_path= filedialog.askdirectory(initialdir="/home/kvsakano/mario-kart/OUTPUT", title="Select folder containing playback_trace CSVs")
root.destroy()
filename = os.path.splitext(os.path.basename(folder_path))[0]


trace_files = sorted(glob.glob(os.path.join(folder_path, "playback_trace*.csv")))
if not trace_files:
    print("No matching files found.")
    exit()


colormap = plt.get_cmap('tab20')


#------------- Plotting the Trace on the Map ------------------

plt.figure(figsize=(10, 10))
plt.imshow(map_img, origin='upper',extent=[0, 4200, 4200, 0],alpha=0.5)
#df = pd.read_csv(trace_files[58])
#plt.plot(df['kart1_X'], df['kart1_Y'], color='black', linewidth=3, alpha=0.5)

"""
i = 0
for file in trace_files:
    df = pd.read_csv(file)
    if 'kart1_X' in df.columns and 'kart1_Y' in df.columns:
        color = colormap(i % colormap.N)
        plt.plot(df['kart1_X'], df['kart1_Y'], color=color, linewidth=3, label=os.path.basename(file), alpha=0.5)
    else:
        print(f"Warning: {file} missing 'kart1_X' or 'kart1_Y' columns. Skipping.")
    i += 1
"""

for file in trace_files:
    df = pd.read_csv(file)
    if 'kart1_X' in df.columns and 'kart1_Y' in df.columns and 'kart1_speed' in df.columns:
        X, Y, speed = df['kart1_X'].values, df['kart1_Y'].values, df['kart1_speed'].values
        for i in range(len(X) - 1):
            if speed[i]>800:
                plt.plot([X[i], X[i+1]], [Y[i], Y[i+1]], color='orangered', linewidth=2.5, alpha=0.2,zorder=10)
            else:
                plt.plot([X[i], X[i+1]], [Y[i], Y[i+1]], color='dodgerblue', linewidth=1.5, alpha=0.2, zorder=5)
            #c = 'orangered' if speed[i] > 900 else 'dodgerblue'
            #plt.plot([X[i], X[i+1]], [Y[i], Y[i+1]], color=c, linewidth=1.5, alpha=0.2)
    else:
        print(f"Warning: {file} missing columns. Skipping.")





"""
#--------------Plotting the Speed over time -----------------
plt.figure(figsize=(10,10))
i = 0
for file in range(1):#trace_files:
    df = pd.read_csv(trace_files[58])
    if 'kart1_speed' in df.columns:
        color = colormap(i % colormap.N)
        plt.plot(np.arange(len(df)), df['kart1_speed'], color=color, linewidth=3, alpha=0.5)
    else:
        print(f"Warning: {file} missing 'kart1_speed' column. Skipping.")
    i += 1
"""

#plt.legend()
plt.title("Mario Trace Overlay on Track Map using model " + filename)
plt.axis('off')  # Turn off pixel axis for clean visuals
plt.show()