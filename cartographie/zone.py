from abc import ABCMeta, abstractmethod , abstractproperty



class Zone:

    __metaclass__=ABCMeta



    @abstractmethod
    def __init__(self,forme):
        pass

    @abstractmethod
    def dessiner(self,fenetre):
        pass
