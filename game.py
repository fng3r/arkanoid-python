import random
from math import pi
from settings import Settings
from bonuses import Bonus
from entities import Ship, Ball, Bullet
from core import Frame, BallState, BlockType, Vector
from level import LevelCreator


class Player:
    def __init__(self):
        self.score = 0
        self.lives = 3

    def gain_life(self):
        self.lives += 1

    def die(self):
        self.lives -= 1

    def get_scores(self, blocks_to_remove):
        for block in blocks_to_remove:
            self.score += 30 * block.type.value


class GameModel:
    def __init__(self, size):
        self.size = size
        self.settings = Settings()
        self.frame = Frame(0, 0, *size)

        self.player = Player()
        self.current_level = 1

        self.reset()
        self.deadly_height = self.ship.bottom - \
            self.ship.frame.height / 2

        self.levels = LevelCreator.get_levels(self.size, self.settings)
        self.won = False
        self.try_get_next_level()

        self.bonuses = set()
        self.bullets = set()

    @property
    def gameover(self):
        return self.player.lives == 0

    @property
    def level_completed(self):
        return len({block for block in self.blocks
                    if block.type != BlockType.Unbreakable}) == 0

    def get_entities(self):
        yield self.ship
        for ball in self.balls:
            yield ball
        for block in self.blocks:
            yield block
        for bullet in self.bullets:
            yield bullet
        for bonus in self.bonuses:
            yield bonus

    def release_ball(self):
        for ball in self.balls:
            if ball.state == BallState.Caught:
                ball.change_state(BallState.Free)
                return True
        return False

    def shooting(self):
        if self.ship.try_shoot():
            self.bullets.add(Bullet(self.ship.left, self.ship.top,
                                    self.settings))
            self.bullets.add(Bullet(self.ship.right, self.ship.top,
                                    self.settings))

    def tick(self, turn_rate=0):
        if self.gameover or self.won:
            return

        if self.level_completed:
            self.player.score += 1000 * self.current_level
            if not self.try_get_next_level():
                return

        old_x = self.ship.left
        self.ship.move(turn_rate)
        self.normalize_ship_location()
        for ball in self.balls:
            ball.move(self.ship.left - old_x)
        self.hold_ball_in_bounds()
        self.check_balls()

        for ball in self.balls:
            blocks_to_remove = {block for block in self.blocks
                                if block.intersects_with(ball)}
            if len(blocks_to_remove) != 0:
                ball.smash_blocks(self, blocks_to_remove)

        self.remove_bonuses()
        self.remove_bullets()

        for ball in self.balls:
            if ball.intersects_with(self.ship):
                mid = self.ship.right - self.ship.width / 2
                ball_mid = ball.right - ball.width / 2
                ball.direction = Vector.from_angle(
                    -pi / 2 + (pi / 2.75 * (ball_mid - mid) /
                               (self.ship.width / 2)))

    def try_get_next_level(self):
        self.current_level += 1
        try:
            self.blocks = next(self.levels)
            self.reset()
            return True
        except StopIteration:
            self.won = True
            return False

    def check_balls(self):
        for ball in self.balls:
            if ball.middle > self.deadly_height:
                self.balls.remove(ball)
        if not self.balls:
            self.kill_player()

    def kill_player(self):
        self.player.die()
        self.reset()

    def reset(self):
        self.bonuses = set()
        self.bullets = set()

        self.ship = Ship((self.size.width - self.settings.ship_size.width) / 2,
                         self.size.height - self.settings.ship_size.height,
                         self.settings)

        self.balls = []
        ball_x = self.ship.x + (self.ship.width -
                                self.settings.ball_size.width) / 2
        ball_y = self.ship.top - self.settings.ball_size.height - 0.01
        ball = Ball(ball_x, ball_y, self.settings)
        ball.stick_to_ship()
        self.balls.append(ball)

    def normalize_ship_location(self):
        self.ship.location = (min(max(0, self.ship.left),
                                  self.frame.right - self.ship.width),
                              self.ship.y)

    def hold_ball_in_bounds(self):
        for ball in self.balls:
            if ball.direction.x > 0 and ball.right > self.frame.right or \
                    ball.direction.x < 0 and ball.x < self.frame.left:
                ball.direction.x = -ball.direction.x

            if ball.direction.y < 0 and ball.y < self.frame.top + 0.1:
                ball.direction.y = -ball.direction.y

    def try_get_bonus(self, block):
        chance = random.random()
        if chance > 0.75:
            bonus_cls = Bonus.get_random_bonus()
            bonus = bonus_cls(block.left, block.top, self.settings)
            self.bonuses.add(bonus)

    def remove_bonuses(self):
        bonuses_to_remove = {bonus for bonus in self.bonuses
                             if not bonus.intersects_with(self)}
        for bonus in self.bonuses:
            bonus.move()
            if bonus.intersects_with(self.ship):
                bonus.activate(self)
                bonuses_to_remove.add(bonus)

        self.bonuses -= bonuses_to_remove

    def remove_bullets(self):
        bullets_to_remove = {bullet for bullet in self.bullets
                             if not bullet.intersects_with(self)}
        blocks_to_remove = set()
        for bullet in self.bullets:
            bullet.move()
            for block in self.blocks:
                if bullet.intersects_with(block):
                    block.get_hit()
                    if block.is_destroyable:
                        blocks_to_remove.add(block)
                    bullets_to_remove.add(bullet)

        self.bullets -= bullets_to_remove
        self.blocks -= blocks_to_remove
