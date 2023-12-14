from color import Colors as C


class Debug:
    def __init__(self, lvl) -> None:
        self.lvl = lvl

    all_true = False
    all_false = True
    skip_factor = 1

    enable_warnings = False

    if skip_factor == 0 and enable_warnings:
        print(C.warning("[DEBUG] WARNING: Cannot set skip_factor to 0. Automatically set to 1"))
        skip_factor = 1

    # Quick init
    # 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
    Q = [0,0,1,0,0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    if all_true:
        for i in range(len(Q)):
            Q[i] = True

    if all_false:
        for i in range(len(Q)):
            Q[i] = False

    # Main Prints [0-2]

    mn_start = bool(Q[0])
    mn_end = bool(Q[1])
    mn_setup = bool(Q[2])

    # Simulation Prints [3-5]

    sim_time_steps = bool(Q[3])
    sim_time_steps_skip = 10000 * skip_factor
    sim_fct_run = bool(Q[4])
    sim_fct_step = bool(Q[5])
    sim_fct_step_skip = 10000 * skip_factor

    # Building [6-11]

    bld_fct_step = bool(Q[6])
    bld_fct_steps_skip = 1000 * skip_factor
    bld_fct_spawn_passenger = bool(Q[7])
    bld_fct_spawn_passenger_steps_skip = 1000 * skip_factor
    bld_spawn_passenger = bool(Q[8])
    bld_spawn_passenger_steps_skip = 1000 * skip_factor
    bld_presses_floor_button = bool(Q[9])
    bld_presses_floor_button_steps_skip = 1000 * skip_factor
    bld_presses_floor_button_up = bool(Q[10])
    bld_presses_floor_button_up_steps_skip = 1000 * skip_factor
    bld_presses_floor_button_down = bool(Q[11])
    bld_presses_floor_button_down_steps_skip = 1000 * skip_factor

    # Floor Prints [12]
    flr_passenger_appended = bool(Q[12])

    # Elevator Prints [13-18]

    elv_fct_step = bool(Q[13])
    elv_fct_steps_skips = 10000 * skip_factor
    if skip_factor == 0:
        elv_fct_steps_skips = 1
    elv_passenger_leaves_elevator = bool(Q[14])
    elv_passenger_leaves_elevator_skips = 10000 * skip_factor
    elv_passenger_enters_elevator = bool(Q[15])
    elv_passenger_enters_elevator_skips = 10000 * skip_factor
    elv_passenger_pressed_button = bool(Q[16])
    elv_passenger_pressed_button_skips = 10000 * skip_factor
    elv_decision_update = bool(Q[17])
    elv_decision_update_skips = 10000 * skip_factor
    elv_movement_update = bool(Q[18])
    elv_movement_update_skips = 10000 * skip_factor

    # Policy Prints [19-22]

    pcy_fct_decide = bool(Q[19])
    pcy_fct_get_action = bool(Q[20])
    pcy_action_update = bool(Q[21])
    pcy_action_update_select = bool(Q[22])
    # Add following integers -2 = MOVE_DOWN, -1 = WAIT_DOWN , 0 = Wait , 1 =
    # WAIT_UP , 2 = MOVE_UP
    pcy_action_update_selection = [0]

    # Distribution Prints [23-26]
    dsr_fct_random_index = bool(Q[23])
    dsr_fct_is_chosen = bool(Q[24])
    dsr_fct_get_index_prob = bool(Q[25])
    tdsr_fct_interpolated_prob = bool(Q[26])

    def pr(level, type, name="", message="", kwargs=[], desc=[], t=-1):
        time_str = ",t = {}".format(t)
        if t == -1:
            time_str = "Time Undefined"
        arg = "[{}:{} {}]".format(type, name, time_str)
        arg = format(arg, ' <5')
        filler = format("", ' <5')
        out = arg + " " + message
        for i in range(len(kwargs)):
            out += ("\n {}{}: {} ").format(filler, desc[i], kwargs[i])
        print(out)

    def str(type, name, message="", kwargs=[], desc=[]):
        arg = "[{}:{}]".format(type, name)
        arg = format(arg, ' <5')
        filler = format("", ' <5')
        out = arg + " " + message
        for i in range(len(kwargs)):
            out += ("\n {}{}: {} ").format(filler, desc[i], kwargs[i])
        return out
