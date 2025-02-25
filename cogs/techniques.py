import os


class Techniques():
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, discription: str, rarity: int):
        try:
            self.name = name
            self.level = level
            self.offense = offense
            self.defense = defense
            self.emote = emote
            self.discription = discription
            self.rarity = rarity
        except Exception as e:
            print("Failed to configure technique \n")

            print(e)

        
    
    