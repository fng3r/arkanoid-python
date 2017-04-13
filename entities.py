import math
import os.path
from functools import reduce
from core import Frame, BallState, BlockType, Vector


class Entity:
    def __init__(self, x, y, size):
        self.frame = Frame(x, y, *size)

    @property
    def x(self):
        return self.frame.x

    @property
    def y(self):
        return self.frame.y

    @property
    def width(self):
        return self.frame.width

    @property
    def height(self):
        return self.frame.height

    @property
    def top(self):
        return self.frame.top

    @property
    def bottom(self):
        return self.frame.bottom

    @property
    def middle(self):
        return self.frame.middle

    @property
    def left(self):
        return self.frame.left

    @property
    def right(self):
        return self.frame.right

    @property
    def center(self):
        return self.frame.center

    @property
    def location(self):
        return self.frame.location

    @location.setter
    def location(self, location):
        self.frame.location = location

    def intersects_with(self, other):
        return self.frame.intersects_with(other.frame)

    def resize(self, d_width, d_height):
        self.frame = self.frame.resize(d_width, d_height)

    def relocate(self, delta_x, delta_y):
        self.frame = self.frame.relocate(delta_x, delta_y)

    def transform(self, delta_x, delta_y, d_width, d_height):
        return self.relocate(delta_x, delta_y).resize(d_width, d_height)

    def get_image(self):
        return os.path.join('images', '%s.png' % type(self).__name__.lower())


class MovingEntity(Entity):
    def __init__(self, x, y, size, velocity, direction):
        super().__init__(x, y, size)
        self.velocity = velocity
        self.direction = Vector.create(direction)

    def move(self, turn_rate=1):
        dir_angle = self.direction.angle
        delta_x = math.cos(dir_angle) * self.velocity * turn_rate
        delta_y = math.sin(dir_angle) * self.velocity * turn_rate
        self.frame = self.frame.relocate(delta_x, delta_y)


class Ship(MovingEntity):
    def __init__(self, x, y, settings):
        super().__init__(x, y, size=settings.ship_size,
                         velocity=settings.ship_velocity,
                         direction=settings.ship_direction)
        self.bullets = 0

    def expand(self):
        self.frame = self.frame.transform(-self.frame.width / 2, 0,
                                          int(self.frame.width / 2), 0)

    def narrow(self):
        self.frame = self.frame.transform(self.frame.width / 2, 0,
                                          -int(self.frame.width / 2), 0)

    def get_ammo(self, count):
        self.bullets += count

    def try_shoot(self):
        if self.bullets > 0:
            self.bullets -= 2
            return True
        return False


class Ball(MovingEntity):
    def __init__(self, x, y, settings):
        super().__init__(x, y, size=settings.ball_size,
                         velocity=settings.ball_velocity,
                         direction=settings.ball_direction)
        self.state = BallState.Free
        self._settings = settings

    @classmethod
    def replicate(cls, instance):
        new_instance = cls(*instance.location, instance._settings)
        new_instance.direction = Vector.create(instance.direction)
        new_instance.velocity = instance.velocity
        new_instance.change_state(instance.state)
        return new_instance

    def stick_to_ship(self):
        self.change_state(BallState.Caught)

    def change_state(self, state):
        self.state = state

    def move(self, delta_x=None):
        if self.state != BallState.Caught:
            super().move()
        else:
            self.frame = self.frame.relocate(delta_x, 0)

    def accelerate(self):
        self.velocity = 1.5 * self._settings.ball_velocity

    def reflect_from_block(self, block):
        if self.state != BallState.Fiery or \
           block.type == BlockType.Unbreakable:
            delta = self.center - block.center
            self.direction = self.direction.normalize()

            if abs(delta.x) - math.cos(self.direction.angle) / 3 * \
                    self.velocity <= block.width / 2:
                self.direction.y = -self.direction.y
            else:
                self.direction.x = -self.direction.x

    def smash_blocks(self, game, blocks_to_remove):
        def vector_min(one, other):
            one_length = (self.center - one.center).length
            other_length = (self.center - other.center).length
            return one if one_length < other_length else other

        block = reduce(lambda acc, item: vector_min(acc, item),
                       blocks_to_remove)
        self.reflect_from_block(block)

        for block in blocks_to_remove:
            block.get_hit()
        removable = {block for block in blocks_to_remove
                     if block.is_destroyable}
        game.blocks -= removable

        if removable:
            game.try_get_bonus(block)
            game.player.get_scores(removable)

    def twin(self, game):
        ball_two = Ball.replicate(self)
        ball_two.direction = ball_two.direction.rotate(-math.pi / 3)
        ball_three = Ball.replicate(self)
        ball_three.direction = ball_three.direction.rotate(math.pi / 3)
        game.balls.append(ball_two)
        game.balls.append(ball_three)

    def get_image(self):
        if self.state != BallState.Fiery:
            return super().get_image()
        else:
            return os.path.join('images', 'fireballbonus.png')


class Bullet(MovingEntity):
    def __init__(self, x, y, settings):
        super().__init__(x, y, size=settings.bullet_size,
                         velocity=settings.bullet_velocity,
                         direction=settings.bullet_direction)


class Block(Entity):
    def __init__(self, x, y, block_type, settings):
        super().__init__(x, y, settings.brick_size)
        self.type = block_type
        self.hits = 0

    def get_hit(self):
        self.hits += 1

    @property
    def is_destroyable(self):
        return self.hits >= self.type.value

    def get_image(self):
        return os.path.join('images', '%sblock' % self.type.name.lower())
