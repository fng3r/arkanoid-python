import os
from entities import Block
from core import BlockType


class LevelCreator:
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'levels')
    block_types = {
        'C': BlockType.Common,
        'S': BlockType.Strong,
        'U': BlockType.Unbreakable,
        '*': None
    }

    @staticmethod
    def get_levels(game_size, settings):
        for level in LevelCreator.create_from_files(game_size, settings):
            yield level

    @staticmethod
    def create_from_files(game_size, settings):
        path = LevelCreator.path
        files = [os.path.join(path, filename) for filename in os.listdir(path)
                 if filename.endswith('.txt')]
        for filename in files:
            with open(filename) as file:
                rows = file.read().split('\n')
                yield LevelCreator.parse_rows(game_size, rows, settings)

    @staticmethod
    def parse_rows(game_size, raw_rows, settings):
        blocks = set()
        row_count = min(12, len(raw_rows))
        column_count = min(12, max([len(row) for row in raw_rows]))
        raw_rows = raw_rows[:row_count]

        width = (game_size.width - column_count *
                 settings.brick_size.width) / 2
        height = 50
        for i in range(row_count):
            row = raw_rows[i]
            for j in range(min(len(row), column_count)):
                block_type = LevelCreator.block_types.get(row[j])
                if block_type:
                    block = LevelCreator._create_block(i, j, width, height,
                                                       block_type, settings)
                    blocks.add(block)
        return blocks

    @staticmethod
    def _create_block(i, j, width, height, block_type, settings):
        block_location = LevelCreator._get_block_location(i, j, width, height,
                                                          settings)
        return Block(*block_location, block_type, settings)

    @staticmethod
    def _get_block_location(i, j, width, height, settings):
        block_x = width + settings.brick_size.width * j
        block_y = height + settings.brick_size.height * i
        return block_x, block_y
