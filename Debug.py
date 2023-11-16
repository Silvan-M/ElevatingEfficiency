class Debug():

    allTrue = False
    allFalse = False

    # Quick init
      #  0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
    Q = [0,0,0,0,0,0,0,0,0,1,1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]

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

    # Simulation Prints []

    simTimeSteps = bool(Q[3])
    simTimeStepsSkip = 10000
    simFctRun = bool(Q[4])
    simFctStep = bool(Q[5])
    simFctStepSkip = 10000
    

    # Building []

    bldFctStep = bool(Q[6])
    bldFctStepsSkip = 1000
    bldFctSpawnPassenger = bool(Q[7])
    bldFctSpawnPassengerStepsSkip = 1000
    bldSpawnPassenger = bool(Q[8])
    bldSpawnPassengerStepsSkip = 1000
    bldPressesFloorButton = bool(Q[9])
    bldPressesFloorButtonStepsSkip = 1000
    bldPressesFloorButtonUp = bool(Q[10])
    bldPressesFloorButtonUpStepsSkip = 1000
    bldPressesFloorButtonDown = bool(Q[11])
    bldPressesFloorButtonDownStepsSkip = 1000


    # FLoor Prints
    flrPassengerAppended =  bool(Q[12])


    psgEntersElevator = bool(Q[1])          
    psgLeavesElevaor = bool(Q[2])

    psgPressesElevatorButton = bool(Q[6])
    psgSpawned = bool(Q[7])

    # Elevator Prints []
    elrStateChanges = bool(Q[8])
    elrStateChangeToMoveDown = bool(Q[9])
    elrStateChangeToWaitUp = bool(Q[10])
    elrStateChangeToWait = bool(Q[11])
    elrStateChangeToWaitDown = bool(Q[12])
    elrStateChangeToMoveUp = bool(Q[13])

    # Distribution Prints
    dsrReturnProb = bool(Q[13])
    dsrIsChoosen = bool(Q[13])

    # Policy Prints

    


    def pr(type, name, message="",kwargs=[],desc=[],t=-1):
        timeStr=",t = {}".format(t)
        if (t ==-1):
            timeStr=""
        arg="[{}:{} {}]".format(type,name,timeStr)
        arg=format(arg, ' <20')
        filler = format("",' <20')
        out=arg+" "+message
        for i in range(len(kwargs)):
            out+=("\n {}{}: {}").format(filler,desc[i],kwargs[i])
        print(out)

    def str(type, name, message="",kwargs=[],desc=[]):
        arg="[{}:{}]".format(type,name)
        arg=format(arg, ' <20')
        filler = format("",' <20')
        out=arg+" "+message
        for i in range(len(kwargs)):
            out+=("\n {}{}: {}").format(filler,desc[i],kwargs[i])
        return out

        



