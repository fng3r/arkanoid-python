import random
from entities import MovingEntity
from core import BallState


class Bonus(MovingEntity):
    def __init__(self, x, y, settings):
        super().__init__(x, y, size=settings.bonus_size,
                         velocity=settings.bonus_velocity,
                         direction=settings.bonus_direction)

    def activate(self, game):
        raise NotImplementedError('This method must be overridden in child \
                                   class implementation')

    @staticmethod
    def get_random_bonus():
        return random.choice(BONUSES)


class DecreaseBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        game.ship.narrow()


class ExpandBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        game.ship.expand()


class BulletBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        game.ship.get_ammo(12)


class FireBallBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        for ball in game.balls:
            ball.change_state(BallState.Fiery)


class FastBallBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        for ball in game.balls:
            ball.accelerate()


class LifeBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        game.player.gain_life()


class DeathBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        game.kill_player()


class TripleBallBonus(Bonus):
    def __init__(self, x, y, settings):
        super().__init__(x, y, settings)

    def activate(self, game):
        random.choice(game.balls).twin(game)


BONUSES = [DecreaseBonus, ExpandBonus, BulletBonus, FireBallBonus,
           FastBallBonus, LifeBonus, DeathBonus, TripleBallBonus]
