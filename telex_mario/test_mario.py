from logging import root

import pandas as pd
import numpy as np
import Tkinter as tk          # Package for UI selection of folders
import tkFileDialog
import tkMessageBox as messagebox

import matplotlib
matplotlib.use('TkAgg')  # explicitly set backend before pyplot import, Tkinter compatible
import matplotlib.pyplot as plt

import telex.synth
import os
import re
import csv

# Note: TeLEX uses python 2.7.18. Some commands like .to_numpy() and filedialog do not exist in this version of python
# Make sure you are using a version compatible package for python!
try:
    import telex.stl as stl_parser
except Exception:
    try:
        import stl as stl_parser
    except Exception:
        stl_parser = None
        print("Warning: no 'stl' parser module found (tried telex.stl and stl). "
              "Fixed (non-parameter) formulas will be skipped unless you install/enable the parser.")



def ask_file_or_folder():
    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)
    win.title("Select Input")

    user_choice = {"choice": None}

    def select_file():
        user_choice["choice"] = "file"
        win.destroy()

    def select_folder():
        user_choice["choice"] = "folder"
        win.destroy()

    tk.Label(win, text="Pick an input type:").pack(pady=10)
    tk.Button(win, text="File", width=10, command=select_file).pack(side="left", padx=20, pady=20)
    tk.Button(win, text="Folder", width=10, command=select_folder).pack(side="right", padx=20, pady=20)

    root.wait_window(win)
    root.destroy()
    return user_choice["choice"]



def import_file(folder_path, root):
    # Load a single trace
    path = tkFileDialog.askopenfilename(initialdir=folder_path, title="Select a file",)
    root.destroy()
    return path

def import_folder(folder_path, root):
    # Load a folder full of traces
    path = tkFileDialog.askdirectory(initialdir=folder_path,  title="Select a folder")
    root.destroy()
    return path   

def preprocessing(path, folder_path):
    filename = os.path.splitext(os.path.basename(path))[0]
    df = pd.read_csv(path)

    # Change the column header of step -> time if it exists
    if 'step' in df.columns:
        df.rename(columns={'step': 'time'}, inplace=True)


    if "phidot" not in df.head():
        print('phidot is not in the dataframe. Calculating and finding it now')

        x_pos = df['kart1_X'].values
        y_pos = df['kart1_Y'].values

        # Smooth x and y before driving velocity (OPTIONAL)
        window = 10
        x_smooth = pd.Series(x_pos).rolling(window, center=True, min_periods=1).mean().values
        y_smooth = pd.Series(y_pos).rolling(window, center=True, min_periods=1).mean().values
        
        # Calculate velocities
        vx = np.gradient(x_smooth)
        vy = np.gradient(y_smooth)

        # Calculate starting reference point by averaging first 10 (x,y)
        x_start = np.mean(x_smooth[:10])
        y_start = np.mean(y_smooth[:10])

        delx = x_smooth - x_start
        dely = y_smooth - y_start
        
        # Mask for elements where either abs(delx)<1 or abs(dely)<1
        mask = (np.abs(delx) < 1) | (np.abs(dely) < 1)

        # phi - set to 0 where mask is True, otherwise arctan2 result. Avoid loop !!!
        phi = np.where(mask, 0, np.arctan2(vx,-vy)) 
        df['phi'] = phi

        # phidot - gradient of phi
        phidot = np.gradient(phi)
        df['phidot'] = phidot


    # add acceleration = difference of kart1_speed between current and previous timestep
    if 'kart1_speed' in df.columns:
        # difference: current - previous; first row will be NaN -> set to 0
        df['acceleration'] = df['kart1_speed'].diff().fillna(0)

    #output_file_path =  folder_path + "/model_08-27/" + filename + "_postprocessed.csv"
    output_file_path =  folder_path + "/model_09-10/" + filename + "_postprocessed.csv"

    df.to_csv(output_file_path, index=False)
    return output_file_path


    
def test_stl_file(file_path, templogicdata):
    print("Performing STL analysis on the file. Hold tight....")

    results = []
    for tlStr in templogicdata:
        try:
            if "?" in tlStr:
                # Parameterized formula -> run synthesis (returns an STL object)
                stlsyn, value, dur = telex.synth.synthSTLParam(tlStr, file_path)
            else:
                # Fixed formula -> try to parse into an STL object
                if stl_parser is None:
                    # no parser available - skip or attempt safe fallback
                    print("Skipping fixed formula (no parser available):", tlStr)
                    results.append({
                        "formula": tlStr,
                        "synthesized stl": None,
                        "theta optimal value": None,
                        "optimization time": None,
                        "test result": None,
                        "robustness": None,
                        "error": "no stl parser available"
                    })
                    continue
                else:
                    # parse the string into the STL object expected by verifySTL
                    stlsyn = stl_parser.parse(tlStr)
                    value, dur = None, None

            # verify (works on the STL object returned by either branch)
            bres, qres = telex.synth.verifySTL(stlsyn, file_path)

            results.append({
                "formula": tlStr,
                "synthesized stl": str(stlsyn),
                "theta optimal value": value,
                "optimization time": dur,
                "test result": bres,
                "robustness": qres,
                "error": None
            })

        except Exception as e:
            print("Error processing formula '{}': {}".format(tlStr, e))
            results.append({
                "formula": tlStr,
                "synthesized stl": None,
                "theta optimal value": None,
                "optimization time": None,
                "test result": None,
                "robustness": None,
                "error": str(e)
            })

    # write CSV as before
    with open("telex_results.csv", "w") as csvfile:
        fieldnames = [
            "formula", "synthesized stl", "theta optimal value",
            "optimization time", "test result", "robustness", "error"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def test_stl_folder(folder_path, templogicdata):
    print("Performing STL analysis on the folder. Hold tight....")

    file_list = [os.path.join(folder_path, f) 
             for f in os.listdir(folder_path) 
             if 'postprocessed' in f]
    results = []

    for file in file_list:
        for tlStr in templogicdata:
            try:
                if "?" in tlStr:
                    stlsyn, value, dur = telex.synth.synthSTLParam(tlStr, file)
                else:
                    if stl_parser is None:
                        print("Skipping fixed formula (no parser available):", tlStr, "on file", file)
                        results.append({
                            "formula": tlStr,
                            "trace": file,
                            "synthesized stl": None,
                            "theta optimal value": None,
                            "optimization time": None,
                            "test result": None,
                            "robustness": None,
                            "error": "no stl parser available"
                        })
                        continue
                    else:
                        stlsyn = stl_parser.parse(tlStr)
                        value, dur = None, None

                bres, qres = telex.synth.verifySTL(stlsyn, file)

                results.append({
                    "formula": tlStr,
                    "trace": file,
                    "synthesized stl": str(stlsyn),
                    "theta optimal value": value,
                    "optimization time": dur,
                    "test result": bres,
                    "robustness": qres,
                    "error": None
                })

            except Exception as e:
                print("Error processing formula '{}' on file '{}': {}".format(tlStr, file, e))
                results.append({
                    "formula": tlStr,
                    "trace": file,
                    "synthesized stl": None,
                    "theta optimal value": None,
                    "optimization time": None,
                    "test result": None,
                    "robustness": None,
                    "error": str(e)
                })

    # write CSV as before
    with open("telex_results.csv", "w") as csvfile:
        fieldnames = [
            "formula", "trace", "synthesized stl", "theta optimal value",
            "optimization time", "test result", "robustness", "error"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def numerical_key(filename):
    # Extract the first number appearing in the filename for sorting
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else -1

def main():
    choice = ask_file_or_folder()
    

    # ----------- ROVER: Mario Kart---------------------------------- (uncomment each of these to test individual rules)
    #templogicdata = ['F[0,1100](lap > 128)'] #------------ Completion within TIme Limit (dropped rule from paper)
    #templogicdata = ['G[0,2000](kart1_speed < 900)']  #------------ Global Speed Limit
    #templogicdata = ['G[0,2000]((surface < 64 | surface > 64) -> F[0,120](surface < 65 & surface > 63))'] #------------ Stay on Track
    #templogicdata = ['G[425,575]((phidot >= 1.0) -> U[0,75]((acceleration > -1 & acceleration < 1), (phidot < 0.04363323129)))'] #------------ Wait to Accelerate (for the first curve)
    
    # Combines all three rules above.
    templogicdata = ['G[0,2000](kart1_speed < 900)', 
                     'G[0,2000]((surface < 64 | surface > 64) -> F[0,120](surface < 65 & surface > 63))', 
                     'G[425,575]((phidot >= 1.0) -> U[0,75]((acceleration > -1 & acceleration < 1), (phidot < 0.04363323129)))']
    

    here = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(here, "data")           
    root = tk.Tk()
    root.withdraw()
    if choice == 'file':
        path = import_file(folder_path, root)
        print(path + " is a CSV file. Checking for phi, will save new file if phi does not exist.")
        path = preprocessing(path, folder_path)
        test_stl_file(path, templogicdata)

    elif choice == 'folder':
        folder_path = import_folder(folder_path, root)
        file_list = [f for f in os.listdir(folder_path) if 'postprocessed' not in f]
        file_list.sort(key=numerical_key)  # sorts in numeric order
        file_list = [os.path.join(folder_path, f) for f in file_list]

        for file in file_list:
            preprocessing(file, folder_path)
        test_stl_folder(folder_path, templogicdata)
        
    else:
        print(path + " is neither a CSV file nor a directory. Try again!")

if __name__ == '__main__':
    main()