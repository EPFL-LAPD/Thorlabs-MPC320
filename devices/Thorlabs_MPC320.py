from pylablib.devices import Thorlabs  # pip install pylablib

class Thorlabs_MPC320(Thorlabs.KinesisMotor):
    """
    Change Log: Leo v2021.06.08 - First version
    
    Leo's subclass for Thorlabs MPC320 - Motorized Fiber Polarization Controller for Ø900 µm Jacket Fiber, 3 Paddles, Ø18 mm
        https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=12896
    Thorlabs APT Communications Protocol
        https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf
    PyLabLib
        https://pylablib.readthedocs.io/en/latest/_modules/pylablib/devices/Thorlabs/kinesis.html#KinesisDevice
    
    Arguments:
        SN: serial number
        ch: 1, 2, or 4 (MPC320 has 3 paddles. ch1 ch2, and ch4')
    
    """
    deg_per_step = 170/1370.0  # MPC320 allow angle range 0-1370 [step], 0-170 [°], deg_per_step≈0.12°
    
    
    def __init__(self, SN, home_before_use=True):
        self.SN = SN
        super().__init__(SN)
        print('\nCreat a SOLO_FiberPaddle object, MPC320')
        print(self.get_device_info())
        self.enable_all_pad()
        if home_before_use:
            self.home_all_pad()
        self.status_update_all()    

    
    def status_update(self, ch=None, do_query=True):
        if do_query:
            data = self.query(0x0490, param1=ch).data   # MGMSG_MOT_REQ_USTATUSUPDATE (0x0490 Thorlabs APT Communications Protocol)
        else:
            data = self.recv_comm(expected_id=0x0491).data   # Don't query, just catch the response message
        chan_ident, = struct.unpack("<h", data[0:2])
        position, = struct.unpack("<l", data[2:6])
        velocity, = struct.unpack("<h", data[6:8])
        motor_current, = struct.unpack("<h", data[8:10])
        status_6bit = data[10:14]
        status_n, = struct.unpack("<I", status_6bit)
        status = [s for (m,s) in self.status_bits if status_n&m]
        # print(data)
        # print(chan_ident, position, velocity, motor_current, status_6bit)
        deg = position*self.deg_per_step
        full_status = [self.SN, chan_ident, position, deg, status]
        print(f'SN={self.SN}, ch={chan_ident}, step={position:4d}, deg={deg:7.3f}, status={status}')
        return full_status
    
    
    def status_update_all(self):
        print('\nUpdating all status...')
        self.status_update(ch=1)
        self.status_update(ch=2)
        self.status_update(ch=4)
    
    
    def wait_until_status(self, sta, exist, ch, timeout=10):
        status = self.status_update(do_query=False)[-1]
        t0 = time.time()
        while True:
            if not any([sta in item for item in status]) ^ (exist):  # XNOR (both same will get true)
                break
            if time.time() - t0 > timeout:  # timeout 10 [sec]
                print(f'Timeout ({timeout}sec)')
                break
            time.sleep(0.1)
            status = self.status_update(ch=ch)[-1]    
    
    
    def enable_all_pad(self):
        print('\nEnabling all paddles (If not enabled previously, it will inevitably go to 85°)...')
        # self.send_comm(0x0210, param1=1, param2=0x01)  # MGMSG_MOD_SET_CHANENABLESTATE (0x0210 Thorlabs APT Communications Protocol)
        # self.send_comm(0x0210, param1=2, param2=0x01)  # param1 is Channel Idents (0x01 channel1, 0x02 channel2, 0x04 channel3, 0x08 channel4) 
        # self.send_comm(0x0210, param1=4, param2=0x01)  # param2 is Enable States (0x01 enable, 0x02 disable)
        self.send_comm(0x0210, param1=7, param2=0x01)    # 1+2+4 = 7 ??
        
        
    def home_all_pad(self):
        print('\nHoming all paddles...')
        status = self.status_update(ch=1)[-1]
        if 'homed' not in status: 
            self.send_comm(0x0443, param1=1)  # MGMSG_MOT_MOVE_HOME (0x0210 Thorlabs APT Communications Protocol)
            self.wait_until_status('homed', True, ch=1)
            self.send_comm(0x0443, param1=2)  # MGMSG_MOT_MOVE_HOME (0x0210 Thorlabs APT Communications Protocol)
            self.wait_until_status('homed', True, ch=2)
            self.send_comm(0x0443, param1=4)  # MGMSG_MOT_MOVE_HOME (0x0210 Thorlabs APT Communications Protocol)
            self.wait_until_status('homed', True, ch=4)
        else:
            print('Already homed')

    

    
    def pad_move_to(self, pos, ch):
        pos = max(0, min(pos,1370))  # allow range 0~1370 [step], 0~170 [°]
        print(f'\nMoving ch{ch} to step={pos} ({pos*self.deg_per_step:.3f}°)...')
        self.move_to(pos, channel=ch)
        self.wait_until_status('moving', False, ch=ch)
    
    
    def pad_move_by(self, delta, ch):
        print(f'\nMoving ch{ch} by delta={delta}...')
        pos = self.status_update(ch=ch)[2]
        print(f'Current step={pos}.', end=' ')
        pos += delta
        pos = max(0, min(pos,1370))  # allow range 0~1370 [step], 0~170 [°]
        print(f'Moving ch{ch} to step={pos} ({pos*self.deg_per_step:.3f}°)...')
        self.move_to(pos, channel=ch)
        self.wait_until_status('moving', False, ch=ch)

   