import math
from collections import namedtuple
from enum import Enum


Size = namedtuple('Size', ['width', 'height'])


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        yield self.x
        yield self.y

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __str__(self):
        return 'x:%s, y:%s' % (self.x, self.y)


class Frame:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def middle(self):
        return self.bottom - int(self.height / 2)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def center(self):
        return Location(self.left + self.width / 2, self.top + self.height / 2)

    @property
    def location(self):
        return Location(self.x, self.y)

    @location.setter
    def location(self, location):
        self.x, self.y = location

    def intersects_with(self, frame):
        return min(self.right, frame.right) >= max(self.left, frame.left) and\
            min(self.bottom, frame.bottom) >= max(self.top, frame.top)

    def resize(self, d_width, d_height):
        return Frame(self.x, self.y,
                     self.width + d_width, self.height + d_height)

    def relocate(self, delta_x, delta_y):
        return Frame(self.x + delta_x, self.y + delta_y,
                     self.width, self.height)

    def transform(self, delta_x, delta_y, d_width, d_height):
        return self.relocate(delta_x, delta_y).resize(d_width, d_height)

    def __str__(self):
        return '(%s, %s), width: %s, height: %s' % (self.x, self.y, self.width,
                                                    self.height)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def create(cls, vector):
        return cls(vector.x, vector.y)

    @classmethod
    def from_angle(cls, angle):
        return cls(math.cos(angle), math.sin(angle))

    def normalize(self):
        length = self.length
        return Vector(self.x / length, self.y / length)

    def rotate(self, angle):
        x = self.x + math.cos(angle)
        y = self.y + math.sin(angle)
        return Vector(x, y)

    @property
    def angle(self):
        return math.atan2(self.y, self.x)

    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)


class BallState(Enum):
    Caught = 0
    Free = 1
    Fiery = 2


class BlockType(Enum):
    Common = 1
    Strong = 3
    Unbreakable = float('inf')


def compare(one, other):
    if one < other:
        return -1
    else:
        return int(one > other)


def sign(number):
    if number == 0:
        return number
    return int(math.copysign(1, number))
