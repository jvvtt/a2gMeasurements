from a2gmeasurements import GimbalRS2
import time
import numpy as np

len_test_2 = 3
test_yaw_angs = [(-180 + np.random.randint(360))*10 for i in range(len_test_2)]
test_yaw_speeds = [25, 30, 35, 40]
which = 2

if which == 1 or which=='ALL':
    input('Start set position incremental mode')
    myGimbal = GimbalRS2(DBG_LVL_0=False, DBG_LVL_1=True)
    myGimbal.start_thread_gimbal()
    print('\nGimbal RS2 thread opened')
    time.sleep(0.01)

    myGimbal.setPosControl(yaw=0, pitch=0, roll=0, ctrl_byte=0x01)
    time.sleep(6)
    for yaw_ang in test_yaw_angs:
        print('\nTEST1: YAW_ANG: ', yaw_ang)
        myGimbal.setPosControl(yaw=int(yaw_ang), pitch=0, roll=0, ctrl_byte=0x00)
        time.sleep(6)

elif which == 2 or which=='ALL':
    input('Start speed test')
    for speed in test_yaw_speeds:
        print('\nActual yaw speed: ', speed)
        myGimbal = GimbalRS2(DBG_LVL_0=False, DBG_LVL_1=True, speed_yaw=speed)
        myGimbal.start_thread_gimbal()
        print('\nGimbal RS2 thread opened')
        
        time.sleep(2)
        myGimbal.setPosControl(yaw=0, pitch=0, roll=0, ctrl_byte=0x01)
        time.sleep(6)

        abs_yaw_ang = 0
        test_passed = []

        for yaw_ang in test_yaw_angs:
            abs_yaw_ang = abs_yaw_ang+yaw_ang
            print('\nTEST2: REL_YAW_ANG: ', yaw_ang, 'ABS_YAW_ANG: ', abs_yaw_ang)
            myGimbal.setPosControl(yaw=int(yaw_ang), pitch=0, roll=0, ctrl_byte=0x00)

            time_2_move = (abs(yaw_ang)/10)/myGimbal.SPEED_YAW
            print('\nTIME2MOVEYAW: ',time_2_move)
            time.sleep(time_2_move + 0.01)
            
            myGimbal.request_current_position()

            if abs_yaw_ang > 1800:
                if abs(myGimbal.yaw*10 - (abs_yaw_ang - 3600)) < 50:
                    test_passed.append(True)
                else:
                    test_passed.append(False)
            elif abs_yaw_ang < -1800:
                if abs(myGimbal.yaw*10 - (3600 - abs_yaw_ang)) < 50:
                    test_passed.append(True)
                else:
                    test_passed.append(False)
            else:
                if abs(myGimbal.yaw*10 - abs_yaw_ang) < 50:
                    test_passed.append(True)
                else:
                    test_passed.append(False)
        
        if sum(test_passed) == len(test_passed):
            print('\nTEST 2 PASSED FOR GIVEN SPEED AND ALL YAW ANGLES')
        else:
            print('\n', sum(test_passed), ' out of ', len(test_passed), ' passed the test')

        myGimbal.stop_thread_gimbal()
        print('\nDisconnecting gimbal')
        time.sleep(0.01)
        myGimbal.actual_bus.shutdown()