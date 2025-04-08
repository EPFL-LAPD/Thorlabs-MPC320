from devices.Thorlabs_MPC320 import Thorlabs_MPC320
# NOTE: MPC320 allow angle range 0-1370 positions. It corresponds to 0-170°.
# NOTE: MPC320 has 3 paddles. ch1 ch2, and ch4


# Method 1: Using with statement (context manager)
with Thorlabs_MPC320(SN='38190824', home_before_use=True) as padboard1, \
        Thorlabs_MPC320(SN='38192094', home_before_use=True) as padboard2, \
        Thorlabs_MPC320(SN='38192044', home_before_use=True) as padboard3:

    padboard1.pad_move_to(pos=200, ch=1)
    padboard1.pad_move_to(pos=600, ch=2)
    padboard1.pad_move_to(pos=800, ch=4)
    padboard2.pad_move_to(pos=200, ch=1)
    padboard2.pad_move_to(pos=600, ch=2)
    padboard2.pad_move_to(pos=800, ch=4)
    padboard3.pad_move_to(pos=200, ch=1)
    padboard3.pad_move_to(pos=600, ch=2)
    padboard3.pad_move_to(pos=800, ch=4)


# Method 2: Using the object directly
padboard1 = Thorlabs_MPC320(SN='38190824', home_before_use=True)
padboard2 = Thorlabs_MPC320(SN='38192094', home_before_use=True)
padboard3 = Thorlabs_MPC320(SN='38192044', home_before_use=True)
padboard1.pad_move_to(pos=200, ch=1)
padboard1.pad_move_to(pos=600, ch=2)
padboard1.pad_move_to(pos=800, ch=4)
padboard2.pad_move_to(pos=200, ch=1)
padboard2.pad_move_to(pos=600, ch=2)
padboard2.pad_move_to(pos=800, ch=4)
padboard3.pad_move_to(pos=200, ch=1)
padboard3.pad_move_to(pos=600, ch=2)
padboard3.pad_move_to(pos=800, ch=4)
padboard1.close()
padboard2.close()
padboard3.close()
