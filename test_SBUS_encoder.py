from a2gmeasurements import SBUSEncoder

list_of_channels = {'MODE': 5, 'TILT': 2, 'ROLL': 4, 'PAN': 1, 'TILT_SPEED': 3, 'PAN_SPEED': 6}

sbus = SBUSEncoder()
sbus.start_sbus()

for key, channel in list_of_channels.items():
    sbus.update_channel(channel, value)