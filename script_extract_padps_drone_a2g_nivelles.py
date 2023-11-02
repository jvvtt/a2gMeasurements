import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import csv

def normalized_pap_dB(irf):
    irf_power = np.power(np.abs(irf),2)
    pap = np.sum(irf_power, axis=2)
    max_pap = np.max(np.max(pap, axis=0),axis=0)
    normalized_pap = 20*np.log10(pap/max_pap)
    
    #print(normalized_pap.shape, normalized_pap.itemsize, normalized_pap.itemsize*normalized_pap.shape[0]*normalized_pap.shape[1])    
    return normalized_pap

plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{{amsmath}}'
ONE_FIGURE_SWITCH = False

rx_sivers_beam_index_mapping_file = open('rx_sivers_beam_index_mapping.csv')
csvreader = csv.reader(rx_sivers_beam_index_mapping_file)
beam_idx_map = [float(i[1]) for cnt,i in enumerate(csvreader) if cnt != 0]
ticks = beam_idx_map[::8]
tickla = [f'{tick:1.2f}°' for tick in ticks]

directory = "C:\\Users\\manifold-uav-vtt\\Documents\\Measurement Files\\Nivelles October 2023\\LoS Drone 2 Ground Open Space Field\\"
filenames = ["2023-10-02-16-33-37-568844-PDPs.npy", "2023-10-02-16-35-09-220217-PDPs.npy"]

Titles_Measurements = [r'$H = 30 [m], D = 52 [m]$',
                       r'$H = 20, D = 1 [m]$']

for cnt, filename_i in enumerate(filenames):
    irf_array = np.load(os.path.join(directory, filename_i))
    normalized_pap = normalized_pap_dB(irf_array)

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(35,40))
    fig.suptitle(Titles_Measurements[cnt], fontsize=60, fontweight='bold', fontfamily='sans-serif')
    pap_plt = ax.imshow(np.transpose(normalized_pap[:, 1:]), aspect=0.7)
    ax.set_ylabel(ylabel="Beamsteering angle [deg]", fontsize=85)
    ax.set_xlabel(xlabel="Time snapshot number", fontsize=85)
    #ax.set_title(Titles_Measurements[cnt], fontsize=60, fontfamily='sans-serif', fontweight="bold")
    ax.yaxis.set_ticks(np.arange(0,64,8))
    ax.yaxis.set_ticklabels(tickla)           
    ax.tick_params(axis='x', labelsize=75)  # Adjust the labelsize as needed
    ax.tick_params(axis='y', labelsize=70)  # Adjust the labelsize as needed    
    cbar = fig.colorbar(pap_plt, ax=ax, shrink=0.8)
    cbar.set_label('Normalized Power [dB]', fontsize=85)
    cbar.ax.tick_params(axis='both', which='both', labelsize=70)  # Adjust labelsize as needed

plt.show()