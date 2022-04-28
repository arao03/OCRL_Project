

def getDefaultObstacleMap(leng,width):
    list1 = [[True]*width]

    for c in range(leng-1):
        list1.append([True]*width)
    for a in range(leng//4,leng//4*2):
        for b in range(width//4,width//4*2):
            list1[a][b]=True
    return list1


