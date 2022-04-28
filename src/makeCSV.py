#five column + five column
#avg info gathered per agent each step 
#avg info gathered per agent until all targets are found
#file name:str(o)+"/"+str(i)+"/"+str(j)+"/"+str(k)+"/"+str(l)+".txt"
#splitmap or not / which map / which set of targets / which set of agent / which trial

def readFile(path):
	with open(path, "rt") as f:
		return f.read()

def writeFile(path, contents):
	with open(path, "wt") as f:
		f.write(contents)


#take in a file name and make its CSV
def makeCSV(directory):
	content = readFile(directory)
	if content == "":
		s = [" " for i in range(31)]
		s=",".join(s)
		return directory+","+s

	content = content.splitlines()
	aboutTime = []
	count = 0
	for l in content:
		if l.startswith("time"):
			aboutTime.append(l)
			count += 1
		else:
			break
	aboutStep = content[count:]

	#collect info about time
	timeL =[str(len(aboutTime))]
	for i in range (len(aboutTime)):
		currLine = aboutTime[i]
		colon = currLine.find(":")
		comma = currLine.find(",")
		currTime = currLine[colon+1:comma]
		timeL.append(currTime)
	while len(timeL) < 11:
		timeL.append(" ")
	timeS = ",".join(timeL)


	#avg info gathered per agent each step 
	stepAvg = [0,0,0,0,0,0,0,0,0,0]
	for stepNum in range(500):
		start = stepNum * 10
		for agent in range (10):
			line = aboutStep[start+agent]
			info = line[line.find("ObservedInfo: ")+14:]
			if len(info) > 0:
				stepAvg[agent] += float(info)
	for agent in range (10):
		stepAvg[agent] = str(stepAvg[agent]/500)
	avg1=','.join(stepAvg)
	

	stepAvg = [0,0,0,0,0,0,0,0,0,0]
	if len(aboutTime) == 10:#all targets are found
		lastLine = aboutTime[-1]
		colon = lastLine.find(":")
		comma = lastLine.find(",")
		lastTime = lastLine[colon+1:comma]
		lastTime = float(lastTime)
		totalSteps = int(lastTime/0.5)
		for stepNum in range(totalSteps):
				start = stepNum * 10
				for agent in range (10):
					line = aboutStep[start+agent]
					info = line[line.find("ObservedInfo: ")+14:]
					stepAvg[agent] += float(info)
		for agent in range (10):
			stepAvg[agent] = str(stepAvg[agent]/totalSteps)
		avg2=','.join(stepAvg)
	else:
		avg2 = avg1
	return directory+","+timeS+","+ avg1 + "," + avg2


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



#open(str(o)+"/"+str(i)+"/"+str(j)+"/"+str(k)+"/"+str(l)+".txt",'w')
def collectCSV(split, maxMap = 33, minMap = 0):
	allCSV=[]
	allCSV.append(makeHeader())
	for mapNum in range(minMap,maxMap):
		for target in range (10):
			for agent in range (3):
				for trial in range(10):
					currName = str(split)+"/"+str(mapNum)+"/"+str(target)+"/"+str(agent)+"/"+str(trial)+".txt"
					print(currName)
					allCSV.append(makeCSV(currName))

	writeFile("output{}.csv".format(split),"\n".join(allCSV))
	return "done"

#try it on my examples
def tryCollectCSV(split):
	allCSV=[]
	allCSV.append(makeHeader())
	for mapNum in range(4):
		for target in range (10):
			for agent in range (3):
				for trial in range(10):
					currName = str(split)+"/"+str(mapNum)+"/"+str(target)+"/"+str(agent)+"/"+str(trial)+".txt"
					allCSV.append(makeCSV(currName))

	writeFile("output.csv","\n".join(allCSV))
	return "done"


if __name__ == '__main__':
	collectCSV(0,33)
	collectCSV(1,33)
