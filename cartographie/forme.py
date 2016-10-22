from abc import ABCMeta, abstractmethod , abstractproperty
import math


class Forme:

    __metaclass__=ABCMeta

    x = None
    y = None

    def distanceAvec(self,forme):
        x=max(self.x,forme.x)-min(self.x,forme.x)
        y=max(self.y,forme.y)-min(self.y,forme.y)
        return math.sqrt(math.pow(x,2)+math.pow(y,2))


    @abstractmethod
    def dessiner(self, fenetre):
        pass
