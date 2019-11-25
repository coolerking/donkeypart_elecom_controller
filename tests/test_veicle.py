# -*- coding: utf-8 -*-
"""
donkeycarパッケージのVehicleフレームワークを使ったテストコード。
"""
def test_manual_recording():
    class ManualRecordingConfig:
        """
        config.py/myconfig.pyモッククラス
        JC-U3912T 自動記録OFF
        """
        DRIVE_LOOP_HZ = 20
        MAX_LOOPS = 10000
        CONTROLLER_TYPE = 'jcu3912t'
        JOYSTICK_THROTTLE_DIR = -1
        JOYSTICK_MAX_THROTTLE = 0.5
        JOYSTICK_STEERING_SCALE = 1.0
        AUTO_RECORD_ON_THROTTLE = False
    cfg = ManualRecordingConfig()
    _run_gamepad(cfg)

def test_auto_recording():
    class AutoRecordingConfig:
        """
        config.py/myconfig.pyモッククラス
        JC-U4113S 自動記録ON
        """
        DRIVE_LOOP_HZ = 20
        MAX_LOOPS = 10000
        CONTROLLER_TYPE = 'jcu4113s'
        JOYSTICK_THROTTLE_DIR = -1
        JOYSTICK_MAX_THROTTLE = 0.5
        JOYSTICK_STEERING_SCALE = 1.0
        AUTO_RECORD_ON_THROTTLE = False
    cfg = AutoRecordingConfig()
    _run_gamepad(cfg)

def _run_gamepad(cfg):
    try:
        from donkeypart_elecom_controller import get_js_controller
    except:
        raise Exception('this test code needs to install donkeypart_elecom_controller via pip')
    part = get_js_controller(cfg)
    class PrintInputs:
        def run(self, angle, throttle, mode, recording):
            print('angle:{} throttle:{}, mode:{}, rec:{}'.format(
                str(angle), str(throttle), str(mode), str(recording),
            ))
    prt = PrintInputs()

    try:
        import donkeycar as dk
    except:
        raise Exception('this test code needs to install donkeycar package')
    V = dk.vehicle.Vehicle()
    import numpy as np
    V.mem['cam/image_array'] = np.zeros((120, 160, 3))
    V.add(part, inputs=['cam/image_array'], outputs=[
        'user/angle', 'user/throttle', 'user/mode', 'recording',
    ], threaded=True)
    V.add(prt, inputs=[
        'user/angle', 'user/throttle', 'user/mode', 'recording',
    ])
    try:
        print('Start test')
        print('Input with gamepad and show standard input')
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)
    except KeyboardInterrupt:
        pass
    print('Stop test')

if __name__ == '__main__':
    # JC-U3912T without auto recording
    test_manual_recording()
    # JC-U4113S with auto recording
    #test_auto_recording()
