class Variable:

    def __init__(self, nom, valeur, max):
        self.nom = nom
        self.valeur = valeur
        self.max = max

    def get(self):
        return self.valeur

    def getMax(self):
        return self.valeur

    def isMax(self):
        return self.valeur >= self.max

    def set(self, valeur):
        self.valeur = valeur

    def incrementer(self,):
        self.valeur += 1
        print(self.nom + " = " + str(self.valeur))

    def decrementer(self,):
        self.valeur -= 1
        print(self.nom + " = " + str(self.valeur))