# GUI global parameters

The variable ``update_vis_time_pap`` has to be higher or equal than the regularity at which ``send_pap_for_vis`` is called. The latter function is called each time the buffer ``hest`` reaches the size given by ``MAX_PAP_BUF_SIZE``. 

For example, for ``MAX_PAP_BUF_SIZE`` $ = 220$ and an average callback time of 100 ms for ``receive_signal_async``, the function ``send_pap_for_vis()`` will be called each 2.2 s.