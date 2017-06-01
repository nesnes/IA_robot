class Condition:

    def __init__(self, type, nom, robot):
        self.nom = nom
        self.type = type
        self.robot = robot
        self.condition = ""
        self.value = 0.0
        self.matchDuration = 0
        self.conditionList = []

    def isTrue(self):
        if self.type == "or":
            for condition in self.conditionList:
                if condition.isTrue():
                    return True
            return False

        elif self.type == "and":
            for condition in self.conditionList:
                if not condition.isTrue():
                    return False
            return True

        elif self.type == "variable":
            variable = self.robot.getVariable(self.nom)
            if variable == None:
                print("WARNING: variable "+self.nom+" not found in objectif conditions")
                return False
            if self.condition == "max":
                return variable.isMax()
            elif self.condition == "notMax":
                return not variable.isMax()
            elif self.condition == "notZero":
                return variable.valeur != 0

        elif self.type == "tempsRestant":
            temps = self.robot.getRunningTime()
            tempsRetsant = self.matchDuration - temps
            if self.condition == "<":
                return tempsRetsant < self.value
            elif self.condition == "<=":
                return tempsRetsant <= self.value
            elif self.condition == ">":
                return tempsRetsant > self.value
            elif self.condition == ">=":
                return tempsRetsant >= self.value
            elif self.condition == "=":
                return tempsRetsant == self.value

        print("WARNING: Unkonwn condition type: "+self.type)
        return False
