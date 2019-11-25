# -*- coding: utf-8 -*-
"""
ELECOM製JC-U3912T/JC-U4113S ワイヤレスゲームパッドコントローラパーツクラス。
また本モジュールが提供するパーツクラスオブジェクトを取得できる
ファクトリのラップ関数も合わせて提供する。

`donkey createjs` でベースクラスを作成し、追記した。
"""
from donkeycar.parts.controller import Joystick, JoystickController

''' ELECOM JC-U3912T '''

class ELECOM_JCU3912T(Joystick):
    """
    JC-T3912Tにおける/dev/input/js0 でのボタン/パッド/ジョイスティック
    各々のコードをマップ化したクラス。
    """
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出し、ボタン・ジョイスティック
        の入力キーを割り当てる。
        引数：
            可変（親クラスJoystic依存）
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)

        # ボタン定義
        self.button_names = {
            # 右ボタン群
            0x130 : '1',    # X square
            0x131 : '2',    # Y triangle
            0x132 : '3',    # A cross
            0x133 : '4',    # B circle
            # 上部ボタン群
            0x134 : '5',    # LT L2
            0x135 : '6',    # RT R2
            0x136 : '7',    # LB L1
            0x137 : '8',    # RB R2
            # アナログスティック押下
            0x138 : '9',    # 左アナログスティック押下
            0x139 : '10',   # 右アナログスティック押下
            # 中央部ボタン群
            0x13a : '11',   # back select
            0x13b : '12',   # start
        }

        # アナログスティック定義
        self.axis_names = {
            # 左アナログスティック
            0x0 : 'left_horz',      # 左アナログ左右
            0x1 : 'left_vert',      # 左アナログ上下
            # 右アナログスティック
            0x2 : 'right_vert',     # 右アナログ上下
            0x5 : 'right_horz',     # 右アナログ左右
            # 十字キー
            0x10 : 'dpad_horz',     # 十字キー左右
            0x11 : 'dpad_vert',     # 十字キー上下
        }

class ELECOM_JCU3912TController(JoystickController):
    """
    JC-U3912T ゲームパッドパーツクラス
    """
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出す。
        引数：
            可変(親クラスJoystickControllerに依存)
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)


    def init_js(self):
        """
        親クラスのコンストラクタから呼び出され、
        ジョイスティック初期化処理を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        try:
            # ボタン定義群が格納されているクラスを生成し、
            # 初期化処理を実行する。
            self.js = ELECOM_JCU3912T(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        """
        ボタンやアナログスティックへ機能を割り当てる。
        引数：
            なし
        戻り値：
            なし
        """
        # ボタン押下時呼び出す関数のマッピング定義 
        self.button_down_trigger_map = {
            # 右ボタン群：上
            '1': self.normal_stop,
            '2': self.erase_last_N_records,

            # 右ボタン群：下
            '3': self.emergency_stop,
            '4': self.toggle_manual_recording,

            # トリガ
            '5': self.decrease_max_throttle,
            '6': self.increase_max_throttle,

            # トリガ小
            '7': self.normal_stop,
            '8': self.normal_stop,

            # アナログスティック押込   
            '9': self.normal_stop,
            '10': self.normal_stop,

            # SELECT 相当
            '11': self.toggle_mode,

            # START相当
            '12': self.toggle_constant_throttle,
        }

        # トリガ型ボタン離脱時呼び出す関数のマッピング定義
        self.button_up_trigger_map = {} # なし

        # アナログ入力時呼び出す関数のマッピング定義
        self.axis_trigger_map = {
            'left_vert':    self.set_throttle,
            'left_horz':    self.set_steering,
            'right_vert':   self.set_throttle,
            'right_horz':   self.set_steering,
            'dpad_horz':    self.move_left_or_right,
            'dpad_vert':    self.move_front_or_rear,
        }

    ''' 親クラスにない機能：マッピング対象の関数 '''

    def normal_stop(self):
        """
        通常停止する。
        引数：
            なし
        戻り値：
            なし
        """
        self.set_throttle(0)
        self.set_steering(0)

    def move_left_or_right(self, axis_val):
        """
        左右へ最大速度で移動する。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        if axis_val > 0:
            self.set_throttle(-1)
            self.set_steering(1)
        elif axis_val < 0:
            self.set_throttle(-1)
            self.set_steering(-1)
        else:
            self.set_throttle(0)
            self.set_steering(0)

    def move_front_or_rear(self, axis_val):
        """
        前後へ最大速度で移動する。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        self.set_steering(0)
        if axis_val > 0:
            self.set_throttle(1)
        elif axis_val < 0:
            self.set_throttle(-1)
        else:
            self.set_throttle(0)

    def set_steering_analog(self, axis_val):
        """
        アナログスティックでステアリング操作を行う。
        十字キーとアナログキーの左右値がことなるため、
        別途実装している。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        return self.set_steering(axis_val * (-1))

''' ELECOM JC-U4113S '''

class ELECOM_JCU4113SJoystick(Joystick):
    """
    JC-U4113Sにおける/dev/input/js0 でのボタン/パッド/ジョイスティック
    各々のコードをマップ化したクラス。
    注意：X-Box互換モードで使用すること。
    """
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出し、ボタン・ジョイスティック
        の入力キーを割り当てる。
        引数：
            可変（親クラスJoystic依存）
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)

        # ボタン入力定義
        self.button_names = {
            # 右ボタン群
            0x133 : '1',    # X
            0x134 : '2',    # Y
            0x130 : '3',    # A
            0x131 : '4',    # B
            # 上部ボタン群
            0x136 : '5',    # LB
            0x137 : '6',    # RB
            # 中央部ボタン群
            0x13a : '11',   # BACK
            0x13b : '12',   # START
            0x13c : '13',   # GUIDE
            # アナログスティック押下
            0x13d : '9',    # 左アナログスティック押下
            0x13e : '10',   # 右アナログスティック押下
        }

        # アナログ入力定義
        self.axis_names = {
            # 左アナログスティック
            0x0 : 'left_horz',  # 左アナログ上下
            0x1 : 'left_vert',  # 左アナログ左右
            # 右アナログスティック
            0x3 : 'right_horz', # 右アナログ上下
            0x4 : 'right_vert', # 右アナログ左右
            # 十字キー
            0x10 : 'dpad_horz', # 十字キー左右
            0x11 : 'dpad_vert', # 十字キー上下
            # 上部ボタン群
            0x2 : '7',          # LT
            0x5 : '8',          # RT
        }

class ELECOM_JCU4113SJoystickController(JoystickController):
    """
    ELECOM社製JC-U4113S XBox互換 ワイヤレスゲームパッド
    パーツクラス
    """
    def __init__(self, *args, **kwargs):
        """
        親クラスのコンストラクタを呼び出す。
        引数：
            可変
        戻り値：
            なし
        """
        super().__init__(*args, **kwargs)


    def init_js(self):
        """
        親クラスのコンストラクタから呼び出され、
        ジョイスティック初期化処理を実行する。
        引数：
            なし
        戻り値：
            なし
        """
        try:
            # ボタンやアナログ入力定義を行う
            self.js = ELECOM_JCU4113SJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        """
        ボタンやアナログスティックへ機能を割り当てる。
        引数：
            なし
        戻り値：
            なし
        """
        # ボタン押下時呼び出す関数のマッピング定義 
        self.button_down_trigger_map = {
            # 右ボタン群：上
            '1':    self.normal_stop,
            '2':    self.erase_last_N_records,
            # 右ボタン群：下
            '3':    self.emergency_stop,
            '4':    self.toggle_manual_recording,
            # トリガ
            '5':    self.decrease_max_throttle,
            '6':    self.increase_max_throttle,
            # トリガ小
            #'7':   self.normal_stop,
            #'8':   self.normal_stop,
            # アナログスティック押込   
            '9':    self.normal_stop,
            '10':   self.normal_stop,
            # SELECT 相当
            '11':   self.toggle_mode,
            # START相当
            '12':   self.toggle_constant_throttle,
            # GUIDE
            '13':   self.emergency_stop,
        }

        # トリガ型ボタン離脱時呼び出す関数のマッピング定義
        self.button_up_trigger_map = {} # なし

        # アナログ入力時呼び出す関数のマッピング定義
        self.axis_trigger_map = {
            # 左アナログスティック
            'left_vert': self.set_throttle,
            'left_horz': self.set_steering,
            # 右アナログスティック
            'right_vert': self.set_throttle,
            'right_horz': self.set_steering,
            # 十字キー
            'dpad_horz': self.move_left_or_right,
            'dpad_vert':    self.move_front_or_rear,
            # 上部ボタン群下のトリガボタン
            '7':            self.normal_stop_axis,
            '8':            self.normal_stop_axis,
        }

    ''' 親クラスにない機能：マッピング対象の関数 '''

    def normal_stop(self):
        """
        通常停止する。
        引数：
            なし
        戻り値：
            なし
        """
        self.set_throttle(0)
        self.set_steering(0)
    
    def normal_stop_axis(self, axis_val):
        """
        押下時に通常停止する。
        引数：
            axis_val    非ゼロ：通常停止
        戻り値：
            なし
        """
        if axis_val != 0:
            self.normal_stop()

    def move_left_or_right(self, axis_val):
        """
        左右へ最大速度で移動する。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        if axis_val > 0:
            self.set_throttle(-1)
            self.set_steering(1)
        elif axis_val < 0:
            self.set_throttle(-1)
            self.set_steering(-1)
        else:
            self.set_throttle(0)
            self.set_steering(0)

    def move_front_or_rear(self, axis_val):
        """
        前後へ最大速度で移動する。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        self.set_steering(0)
        if axis_val > 0:
            self.set_throttle(1)
        elif axis_val < 0:
            self.set_throttle(-1)
        else:
            self.set_throttle(0)

    def set_steering_analog(self, axis_val):
        """
        アナログスティックでステアリング操作を行う。
        十字キーとアナログキーの左右値がことなるため、
        別途実装している。
        引数：
            axis_val    ゼロ：停止
        戻り値：
            なし
        """
        return self.set_steering(axis_val * (-1))

def get_js_controller(cfg):
    """
    myconfig.py上にて指定されたCONTROLLER_TYPE値にあわせて
    ジョイスティックコントローラパーツを生成し、
    オブジェクトを返却するファクトリ関数。
    引数：
        cfg config.py/myconfig.py にて指定された定義をインスタンス変数として
            参照できるオブジェクト
    戻り値
        ctr ジョイスティックパーツクラス
    """
    try:
        # donkeycar パッケージ側のファクトリ関数を実行
        from donkeycar.parts.controller import get_js_controller as get_controller
        return get_controller(cfg)
    except:
        '''
        標準のファクトリ関数では該当するCONTROLLER_TYPEが存在しなかった場合
        '''
        if cfg.CONTROLLER_TYPE == "jcu3912t":
            '''
            ELECOM JC-U3912T コントローラの場合
            '''
            cont_class = ELECOM_JCU3912TController
            ctr = cont_class(throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                                throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
                                steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                                auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
            ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
            return ctr
        elif cfg.CONTROLLER_TYPE == "jcu4113s":
            '''
            ELECOM JC-U4113S(X-Direct) コントローラの場合 
            '''
            cont_class = ELECOM_JCU4113SJoystickController
            ctr = cont_class(throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
                                throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
                                steering_scale=cfg.JOYSTICK_STEERING_SCALE,
                                auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE)
            ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
            return ctr
        else:
            raise
    
    
    