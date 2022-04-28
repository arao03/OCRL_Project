import entity


class EntityManager():

    def __init__(self):
        self.entityList = []
        self.nextId = 0


    def tick(self, deltaTime, world):
        for ent in self.entityList:
            ent.tick(deltaTime, world)

    def spawnEntity(self, entityClass, position = (0,0), angle = 0):
        newEntity = entityClass( position, angle, self.nextId)
        newEntity.onSpawned()
        self.nextId += 1
        self.entityList.append(newEntity)
        return newEntity

    def getEntityById(self, id):
        for ent in self.entityList:
            if id == ent.id:
                return ent
        return None

    def destroyEntity(self, id):
        for ent in self.entityList:
            if id == ent.id:
                ent.onDestroy()
                self.entityList.remove(ent)
                return True
        return False