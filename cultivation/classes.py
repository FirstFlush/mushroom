


class FreezerBag():
    '''All weights in grams (g)'''

    silica_weight = 5.475

    def __init__(self, bag_weight=13.5, silica_packs=2):
        
        self.bag_weight = bag_weight
        self.silica_packs = silica_packs
        self.weight = self.bag_weight + self.silica_weight * self.silica_packs
        
        return