import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
import csv
import argparse

def normalized_pap_dB(irf):
    irf_power = np.power(np.abs(irf),2)
    pap = np.sum(irf_power, axis=2)
    max_pap = np.max(np.max(pap, axis=0),axis=0)
    normalized_pap = 20*np.log10(pap/max_pap)
    
    #print(normalized_pap.shape, normalized_pap.itemsize, normalized_pap.itemsize*normalized_pap.shape[0]*normalized_pap.shape[1])    
    return normalized_pap

parser = argparse.ArgumentParser(description='Displays figures for measurement campaign')
parser.add_argument('--sizeTitle', type=int, default=50, help='Font size of the title')
parser.add_argument('--sizeXaxisTitle', type=int, default=40, help='Font size of the X-axis label')
parser.add_argument('--sizeYaxisTitle', type=int, default=40, help='Font size of the Y-axis label')
parser.add_argument('--sizeLegend', type=int, default=45, help='Font size of the legend')
parser.add_argument('--sizeTickAxis', type=int, default=40, help='Font size of the ticks in both axes')
parser.add_argument('--pathToMeasFolder', type=str, default="../../Nivelles October 2023", help="Path to the 'Nivelles October 2023' folder")
args = parser.parse_args()

plt.rcParams['text.usetex'] = True
plt.rcParams['text.latex.preamble'] = r'\usepackage{{amsmath}}'
ONE_FIGURE_SWITCH = False

rx_sivers_beam_index_mapping_file = open('../data/rx_sivers_beam_index_mapping.csv')
csvreader = csv.reader(rx_sivers_beam_index_mapping_file)
beam_idx_map = [float(i[1]) for cnt,i in enumerate(csvreader) if cnt != 0]
ticks = beam_idx_map[::8]
tickla = [f'{tick:1.2f}°' for tick in ticks]

#directory = "C:\\Users\\manifold-uav-vtt\\Documents\\Measurement Files\\Nivelles October 2023\\V2V"
#directory = "D:\\Measurement Files\\Nivelles October 2023\\V2V"
directory = args.pathToMeasFolder + "/V2V"

n_time_snaps_file = []
dates_last_irf_array_per_measurement = []
irfs_in_measurement_i = []
irfs_per_measuremment_list = []

V2V_Measurement_Titles = [r"$\alpha_{TX} = 0, \alpha_{RX} =  0$",
                          r"$\alpha_{TX} = -15, \alpha_{RX} = 0$",
                          r'$\alpha_{TX} = -30, \alpha_{RX} = 0$',
                          r'$\alpha_{TX} = 15, \alpha_{RX} = 0$',
                          r'$\alpha_{TX} = 30, \alpha_{RX} = 0$',
                          r'$\alpha_{TX} = 0, \alpha_{RX} = -14$',
                          r'$\alpha_{TX} = 0, \alpha_{RX} = -31$',
                          r'$\alpha_{TX} = -15, \alpha_{RX} = -15$',
                          r'$\alpha_{TX} = 0, \alpha_{RX} = 0$']

OPEN_FIELD_Measurement_Titles = [r'$\alpha_{TX} = 0, \alpha_{RX} = 0, D = 2.65 [m]$',
                                 r'$\alpha_{TX} = 0, \alpha_{RX} = 0, D = 9 [m]$',
                                 r'$\alpha_{TX} = 0, \alpha_{RX} = 0, D = 1 [m]$']

#plt.rcdefaults()

if ONE_FIGURE_SWITCH:
    fig1, ax1 = plt.subplots(ncols=3, nrows=3, figsize=(40,27))
    fig1.suptitle("V2V Measurements", fontsize=13, fontweight='bold', fontfamily='sans-serif')
    fig2, ax2 = plt.subplots(ncols=3, nrows=1)
    fig2.suptitle("Open space close measurements", fontsize=13, fontweight='bold', fontfamily='sans-serif')
cnt = 0
cnt2 = 0
for filename_i in os.listdir(directory):
    if "Readme" in filename_i:
        continue
       
    irf_array_i = np.load(os.path.join(directory, filename_i))
    t_snaps = irf_array_i.shape[0]
    n_time_snaps_file.append({'snaps':t_snaps, 'name': filename_i})
    
    irfs_in_measurement_i.append(irf_array_i)
    #dates_created_file.append(datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(directory, filename_i))))   
    
    # Each time the array is less than 250 it means that the measurement was finishing
    if t_snaps != 250:
        aux = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(directory, filename_i)))
        dates_last_irf_array_per_measurement.append(aux)
        tmp = np.concatenate(irfs_in_measurement_i)
        irfs_per_measuremment_list.append(tmp)
        
        print('Snaps: ', tmp.shape[0])
        print('Date las irf file: ', aux)
        
        normalized_pap = normalized_pap_dB(tmp)
        
        irfs_in_measurement_i = []
        
        if cnt < 9:                
            if ONE_FIGURE_SWITCH:
                (r, c) = divmod(cnt, 3)
                pap_plt = ax1[r,c].imshow(normalized_pap[:, 1:], aspect=0.05)
                ax1[r, c].set_xlabel(xlabel="Beamsteering angle [deg]")
                ax1[r, c].set_ylabel(ylabel="Time snapshot number")
                ax1[r,c].set_title(V2V_Measurement_Titles[cnt], fontsize=12, fontfamily='sans-serif')
                ax1[r,c].xaxis.set_ticks(np.arange(0, 64, 8))
                ax1[r,c].xaxis.set_ticklabels(tickla)
                    #ax1[r,c].set_xlim((beam_idx_map[1], beam_idx_map[-1]))

                fig1.colorbar(pap_plt, ax=ax1[r,c], label='Normalized Power [dB]')
                
            else:
                print("Here")
                fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(27,40))
                #fig.suptitle("V2V Measurements", fontsize=, fontweight='bold', fontfamily='sans-serif')
                pap_plt = ax.imshow(np.transpose(normalized_pap[:, 1:]), aspect=10)
                ax.set_ylabel(ylabel="Beamsteering angle [deg]", fontsize=args.sizeXaxisTitle)
                ax.set_xlabel(xlabel="Time snapshot number", fontsize=args.sizeYaxisTitle)
                ax.set_title(V2V_Measurement_Titles[cnt], fontsize=args.sizeTitle, fontfamily='sans-serif', fontweight="bold")
                ax.yaxis.set_ticks(np.arange(0, 64, 8))
                ax.yaxis.set_ticklabels(tickla)
                ax.tick_params(axis='x', labelsize=args.sizeTickAxis)  # Adjust the labelsize as needed
                ax.tick_params(axis='y', labelsize=args.sizeTickAxis)  # Adjust the labelsize as needed
                cbar = fig.colorbar(pap_plt, ax=ax, shrink=0.8)
                cbar.set_label('Normalized Power [dB]', fontsize=args.sizeLegend)
                cbar.ax.tick_params(axis='both', which='both', labelsize=args.sizeTickAxis)  # Adjust labelsize as needed
        else:
            if ONE_FIGURE_SWITCH:    
                pap_plt = ax2[cnt2].imshow(normalized_pap[:, 1:], aspect=0.1)
                ax2[cnt2].set_xlabel(xlabel="Beamsteering angle [deg]")
                ax2[cnt2].set_ylabel(ylabel="Time snapshot number")
                ax2[cnt2].set_title(OPEN_FIELD_Measurement_Titles[cnt2], fontsize=12, fontfamily='sans-serif')
                ax2[cnt2].xaxis.set_ticks(np.arange(0,64,8))
                ax2[cnt2].xaxis.set_ticklabels(tickla)
                fig2.colorbar(pap_plt, ax=ax2[cnt2], label='Normalized Power [dB]')
                plt.subplots_adjust(left=0.05,
                            bottom=0.1, 
                            right=0.9, 
                            top=0.9, 
                            wspace=0.4, 
                            hspace=0.2)
            else:
                fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(27,40))
                #fig.suptitle("Open space close measurements", fontsize=45, fontweight='bold', fontfamily='sans-serif')
                pap_plt = ax.imshow(np.transpose(normalized_pap[:, 1:]), aspect=10)
                ax.set_ylabel(ylabel="Beamsteering angle [deg]", fontsize=args.sizeXaxisTitle)
                ax.set_xlabel(xlabel="Time snapshot number", fontsize=args.sizeYaxisTitle)
                ax.set_title(OPEN_FIELD_Measurement_Titles[cnt2], fontsize=args.sizeTitle, fontfamily='sans-serif', fontweight="bold")
                ax.yaxis.set_ticks(np.arange(0,64,8))
                ax.yaxis.set_ticklabels(tickla)           
                ax.tick_params(axis='x', labelsize=args.sizeTickAxis)  # Adjust the labelsize as needed
                ax.tick_params(axis='y', labelsize=args.sizeTickAxis)  # Adjust the labelsize as needed    
                cbar = fig.colorbar(pap_plt, ax=ax, shrink=0.8)
                cbar.set_label('Normalized Power [dB]', fontsize=args.sizeLegend)
                cbar.ax.tick_params(axis='both', which='both', labelsize=args.sizeTickAxis)  # Adjust labelsize as needed
            cnt2 = cnt2+1
        cnt = cnt + 1     

plt.show()