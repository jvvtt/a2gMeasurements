# Installations

## Requirements Python

Below is the list of required python packages with their respective versions:

<div class="center-table" markdown>
| Package name | Version | 
| :------------: | :--------------------: | 
| scipy  | 1.11.1 | 
| scikit-learn | 1.3.0 |
| numpy | 1.26.1 |
| crc | 2.0.0 |
| python-can | 4.0.0 |
| pynmea2 | 1.18.0 |
| pyserial | 3.5.0 |
| fastapi | 0.109.2 |
| paramiko | 3.2.0 |
| uvicorn | 0.27.1 |
| folium | 0.15.1 |
| scikit-learn | 1.3.0 |

</div>

## Requirements Planning Tool

1. 
```sh
npm install --save fs-extra
```

# Git
In the ``.gitignore`` file the ``data`` folder is added to avoid uploading the measured files, since there can be synch troubles due to their size.

Measurement files (in the receiver node) will still be saved in the ``data`` but won't be uploaded to the Github of the project, as stated before.
