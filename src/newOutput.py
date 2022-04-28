#one line target found: 1st{time:(x,y)}, 2st ....10 (may be shorter)

def exportRawOutput(simulationData, sim):
    allRecorded=sim.pathPlanner.recordedObservations #index --> time
    notFound=sim.pathPlanner.observations
    observationInfo=[]
    targetsPosition=[]
    

    for currObservation in allObservations:
        found = currObservation[1]
        time = currObservation[0][0]
        x = currObservation[0][1]#target position x
        y = currObservation[0][2]#target position y
        currInfo = [x,y,time]
        #currInfo = "time:"+str(time)+(", found target at(%f,%f)" %(x,y))
        if found ==1 and ((x,y) not in targetsPosition):
            observationInfo.append(currInfo)
            targetsPosition.append((x,y))

    for currObservation in notFound:
        time = currObservation[0][0]
        x = currObservation[0][1]#target position x
        y = currObservation[0][2]#target position y
        currInfo = [x,y,-1]
        if (x,y) not in targetsPosition:
            observationInfo.append(currInfo)
            targetsPosition.append((x,y))
    #len(targetsPosition) == 10 (please)



    #each step a line:agent0 position, agent1 position, agent2....agent 10 position
    #500 lines
    stepInfo = []
    a = sim.recordedAgentData
    for i in range(0, len(a)):#i: number of step, 
        agentInfo = []
        for j in range(0, len(a[i])):
            (id,(x,y),z) = a[i][j]
            #id:agent id, (x,y)position, z: info gathered
            #agentInfo.append("Step: "+ str(i) + " AgentID: "+str(id)+" Position: ("+str(x)+","+str(y)+") ObservedInfo: " +str(z))
            agentInfo.append([x,y,z])
        stepInfo.append(agentInfo)


    out = []
    out.append(observationInfo)#len(observationInfo)=10
    out.append(stepInfo)#len(stepInfo)=500

    return out




#step number, agent0 position, agent1 position, agent2....agent 10 position
def exportTxt(out):
    observationInfo = out[0]
    infoStr = str(observationInfo)
    stepInfo = out[1:]#len(stepInfo)=500
    for i in range(500):
        curr = stepInfo[i]#len(curr) = 10: 10 agents
        infoStr = infoStr + "\n" + str(curr)
    return infoStr

#create CSV
def makeHeader():
    header=["directory", "number of targets found"]
    header.append(" time the 1st target was found")
    header.append(" time the 2nd target was found")
    header.append(" time the 3st target was found")
    for i in range(4,11):
        s = " time the %d" % i
        s = s + "th target was found"
        header.append(s)
    for i in range(10):
        header.append(" average info agent %d gathered each step" % i)
    for i in range(10):
        header.append(" before all targets are found average info agent %d gathered each step" % i)

    return ','.join(header)

def exportCSV(out, fileName):
    observationInfo = out[0]
    infoStr = str(observationInfo)
    stepInfo = out[1:]#len(stepInfo)=500

    #time and place where targets found

    foundNum = 0
    timeL = [foundNum]
    for observation in observationInfo:
        x = observation[0]
        y = observation[1]
        currTime = observation[2]
        if time != -1:
            foundNum += 1
            timeL.append(currTime)
    timeL[0] = foundNum
    while len(timeL) < 11:
        timeL.append(" ")
    timeS = ",".join(timeL)

    #avg info gathered per agent each step 
    stepAvg = [0,0,0,0,0,0,0,0,0,0]
    for i in range(500):
        currStepInfo = stepInfo[i]
        for id in range (10):
            x = currStepInfo[0]
            y = currStepInfo[1]
            info = currStepInfo[2]
            stepAvg[id] += info
    for id in range (10):
        stepAvg[agent] = str(stepAvg[agent]/500)
    avg1=','.join(stepAvg)

    stepAvg = [0,0,0,0,0,0,0,0,0,0]
    if foundNum == 10:
        lastTargetFound = observationInfo[-1]
        lastTime = lastTargetFound[-1]
        totalSteps = int(lastTime/0.5)
        for i in range(totalSteps):
            for id in range (10):
                x = currStepInfo[0]
                y = currStepInfo[1]
                info = currStepInfo[2]
                stepAvg[id] += info
        for id in range (10):
            stepAvg[agent] = str(stepAvg[agent]/totalSteps)
        avg2=','.join(stepAvg)
    else:
        avg2 = avg1
    S = makeHeader()
    S = S + "\n" + fileName + "," + timeS + "," + avg1 + "," + avg2

    return S


    















