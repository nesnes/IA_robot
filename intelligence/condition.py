from action import Action

class Condition:

    def __init__(self, type, nom, robot):
        self.nom = nom
        self.type = type
        self.robot = robot
        self.condition = ""
        self.value = 0.0
        self.inverted = False
        self.matchDuration = 0
        self.conditionList = []

    def isTrue(self):
        result = False
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
                result = variable.isMax()
            elif self.condition == "notMax":
                result = not variable.isMax()
            elif self.condition == "notZero":
                result = variable.valeur != 0

        elif self.type == "tempsRestant":
            temps = self.robot.getRunningTime()
            tempsRetsant = self.matchDuration - temps
            if self.condition == "<":
                result = tempsRetsant < self.value
            elif self.condition == "<=":
                result = tempsRetsant <= self.value
            elif self.condition == ">":
                result = tempsRetsant > self.value
            elif self.condition == ">=":
                result = tempsRetsant >= self.value
            elif self.condition == "=":
                result = tempsRetsant == self.value

        elif self.type == "function":
            action = Action(self.nom,"",[],[])
            result = self.robot.executer(action)

        else:
            print("WARNING: Unkonwn condition type: " + self.type)
            return False

        if self.inverted:
            return not result
        else:
            return result
