from core import Size, Vector


class Settings:
    ball_size = Size(35, 35)
    ship_size = Size(200, 25)
    bonus_size = Size(25, 25)
    brick_size = Size(100, 30)
    bullet_size = Size(10, 20)

    ball_velocity = 15
    ship_velocity = 17
    bonus_velocity = 10
    bullet_velocity = 13

    ball_direction = Vector(-0.5, -0.5)
    ship_direction = Vector(0, 0)
    bonus_direction = Vector(0, 1)
    bullet_direction = Vector(0, -1)
