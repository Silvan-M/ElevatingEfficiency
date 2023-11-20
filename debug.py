class Debug():
    def __init__(self,lvl) -> None:
        self.lvl=lvl

    allTrue = False
    allFalse = False
    skipFactor = 0

    # Quick init
      #  0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
    Q = [0,0,1,0,0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    if(allTrue):
        for i in range(len(Q)):
            Q[i]=True
    
    if(allFalse):
        for i in range(len(Q)):
            Q[i]=False

    # Main Prints [0-2]

    mnStart = bool(Q[0]) 
    mnEnd = bool(Q[1]) 
    mnSetup = bool(Q[2]) 

    # Simulation Prints [3-5]

    simTimeSteps = bool(Q[3])
    simTimeStepsSkip = 10000 * skipFactor
    simFctRun = bool(Q[4])
    simFctStep = bool(Q[5])
    simFctStepSkip = 10000 * skipFactor
    

    # Building [6-11]

    bldFctStep = bool(Q[6])
    bldFctStepsSkip = 1000 * skipFactor
    bldFctSpawnPassenger = bool(Q[7])
    bldFctSpawnPassengerStepsSkip = 1000 * skipFactor
    bldSpawnPassenger = bool(Q[8])
    bldSpawnPassengerStepsSkip = 1000 * skipFactor
    bldPressesFloorButton = bool(Q[9])
    bldPressesFloorButtonStepsSkip = 1000 * skipFactor
    bldPressesFloorButtonUp = bool(Q[10])
    bldPressesFloorButtonUpStepsSkip = 1000 * skipFactor
    bldPressesFloorButtonDown = bool(Q[11])
    bldPressesFloorButtonDownStepsSkip = 1000 * skipFactor


    # FLoor Prints [12]
    flrPassengerAppended =  bool(Q[12])

    # Elevator Prints [13-18]

    elvFctStep = bool(Q[13])
    elvFctStepsSkips = 10000 * skipFactor
    if (skipFactor == 0):
        elvFctStepsSkips = 1
    elvPassengerLeavesElevator = bool(Q[14])
    elvPassengerLeavesElevatorSkips = 10000 * skipFactor
    elvPassengerEntersElevator = bool(Q[15]) 
    elvPassengerEntersElevatorSkips = 10000 * skipFactor
    elvPassengerPressedButton = bool(Q[16]) 
    elvPassengerPressedButtonSkips = 10000 * skipFactor
    elvDecisionUpdate = bool(Q[17]) 
    elvDecisionUpdateSkips = 10000 * skipFactor
    elvMovementUpdate = bool(Q[18]) 
    elvMovementUpdateSkips = 10000 * skipFactor


    # Policy Prints [19-22]
    
    pcyFctdecide = bool(Q[19])
    pcyFctGetAction = bool(Q[20])
    pcyActionUpdate = bool(Q[21])
    pcyActionUpdateSelect = bool(Q[22])
    pcyActionUpdateSelection = [0]  # Add following integers -2 = MoveDown, -1 = WaitDown , 0 = Wait , 1 = WaitUp , 2 = MoveUp 



    # Distribution Prints [23-26]
    dsrFctRandomIndex = bool(Q[23])
    dsrFctIsChosen = bool(Q[24])
    dsrFctgetIndexProb = bool(Q[25])
    tdsrFctInterpolatedProb = bool(Q[26])


    

    


    def pr(level,type, name, message="",kwargs=[],desc=[],t=-1):
        timeStr=",t = {}".format(t)
        if (t ==-1):
            timeStr=""
        arg="[{}:{} {}]".format(type,name,timeStr)
        arg=format(arg, ' <5')
        filler = format("",' <5')*(level+1)
        out=arg+" "+message
        for i in range(len(kwargs)):
            out+=("\n {}{}: {} ").format(filler,desc[i],kwargs[i])
        print(out)

    def str(type, name, message="",kwargs=[],desc=[]):
        arg="[{}:{}]".format(type,name)
        arg=format(arg, ' <5')
        filler = format("",' <5')
        out=arg+" "+message
        for i in range(len(kwargs)):
            out+=("\n {}{}: {} ").format(filler,desc[i],kwargs[i])
        return out
    

        



