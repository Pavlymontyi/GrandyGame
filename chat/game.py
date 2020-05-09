
class Game(object):

    def __init__(self):
        self.piles = []

if __name__ == "__main__":
    game = Game()
    print(str(game))
    print(str(game.piles))

    game.piles.append(7)
    print(str(game.piles))

    game.piles.append(3)
    print(str(game.piles))


    if (game.piles.__contains__(7)):
        game.piles.remove(7)
        game.piles.append(3)
        game.piles.append(4)

    print(game.piles)
    y = 7
    # for x in game.piles:



