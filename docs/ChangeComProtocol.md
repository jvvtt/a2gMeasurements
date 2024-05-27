# Communication protocol

It is possible to extend the communication protocol by implementing new functionality in the methods ``encode_message()``, ``socket_send_cmd()`` and ``decode_message()`` in the class ``HelperA2GMeasurements`` of the file ``a2gmeasurements.py``.

New functionality means new messages exchanged between both nodes. As to now, there are three types of messages implemented (shown under row ``message_type`` in one of the Tables in [Communication protocol](CommunicationProtocol.md#communication-protocol). 

New messages introduced by the developer can be:

1. Short messages without requiring any answer back from the receiver.
2. Short messages that require an answer from the receiver.
3. Long messages without requiring the answer from the receiver (long messages make use of the ``data`` field of the communication process to send additional data, i.e. a vector with channel impulse response related information)

!!! success "Acknowledgements"
    Be aware that as there is a TCP connection established, the acknowledgement/answer messsages mentioned previously refer to  additional acknowledgement/answer messages on top (at the application layer) of the handshake and acknowledgement process used by TCP at its communication layer. 

Developers need to modify ``encode_message()``, as shown in the following snippet of code:

!!! failure "Change encoder to extend available messages"
    ```py
    def encode_message(self, source_id, destination_id, message_type, cmd, data=None):
        if message_type == 0x01: 
        //...
            elif cmd == 0x0A:
            # INSERT HERE HOW TO ENCODE YOUR NEW MESSAGE IF IT IS A SHORT MESSAGE WITHOUT ANSWER FROM THE RECEIVER
        elif message_type == 0x02:
        //...
            elif cmd == 0x02:
            # INSERT HERE HOW TO ENCODE YOUR NEW MESSAGE IF IT IS A LONG MESSAGE WITHOUT ANSWER FROM THE RECEIVER
        elif message_type == 0x03:
        //...
            elif cmd == 0x02:
            # INSERT HERE HOW TO ENCODE YOUR NEW MESSAGE IF IT IS A MESSAGE REQUIRING AN ANSWER FROM THE RECEIVER    
    ```

Then modify ``decode_message()``, as shown in the following snippet:

!!! failure "Change decoder to extend available messages"
    ```py
    def decode_message(self, data):
        if message_type == 0x01: 
        # ...
            elif cmd == 0x0A:
            # INSERT HERE HOW TO DECODE YOUR NEW MESSAGE IF IT IS A SHORT MESSAGE WITHOUT ANSWER FROM THE RECEIVER. # IT SHOULD MATCH THE ENCODING FORMAT
        elif message_type == 0x02:
        # ...
            elif cmd == 0x02:
            # INSERT HERE HOW TO DECODE YOUR NEW MESSAGE IF IT IS A LONG MESSAGE WITHOUT ANSWER FROM THE RECEIVER
            # IT SHOULD MATCH THE ENCODING FORMAT
        elif message_type == 0x03:
        # ...
            elif cmd == 0x02:
            # INSERT HERE HOW TO DECODE YOUR NEW MESSAGE IF IT IS A MESSAGE REQUIRING AN ANSWER FROM THE RECEIVER
            # IT SHOULD MATCH THE ENCODING FORMAT
    ```

Finally, modify ``socket_send_cmd()``. This method is a wrapper for the ``encode_message()`` method, and assigns a string name to each message, so that it is easier to identify them:

!!! failure "Change socket sender to extend available messages"
    ```py
    def socket_send_cmd(self, type_cmd=None, data=None):
        if type_cmd == 'SETGIMBAL': 
        # ...
        elif type_cmd == '': # ENTER HERE THE NAME WITH WHICH YOU WILL IDENTIFY THE NEW MESSAGE
            frame = self.encode_message(source_id= , destination_id= ,message_type= , cmd= , data= ,) 
            # FILL THE PREVIOUS LINE WITH THE CORRESPONDING INFORMATION FOR THE NEW MESSAGE
    ```