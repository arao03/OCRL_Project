

'''#reportObservation in pathprimitiveplanner.py

reportObservation(self, agent, observation)

#observation: [time,x,y]

simulationData.pathPlanner.observations

#simulation data'''

def exportObservations(simulationData):
    allObservations=simulationData.pathPlanner.observations#index --> time
    observationInfo=[]
    targetsFound=[]
    for currObservation in allObservations:
        found = currObservation[1]
        time = currObservation[0][0]
        x=currObservation[0][1]#target position x
        y=currObservation[0][2]#target position y
        currInfo = "time:"+str(time)+(", found target at(%f,%f)" %(x,y))
        if found == 1 && (x,y) not in targetsFound:
            observationInfo.append(currInfo)
            targetsFound.append((x,y))
    observationText="\n".join(observationInfo)
    return observationText




