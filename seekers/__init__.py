from .seekers_types import *
from . import game_logic, draw

from typing import Iterable
import os
import glob
import pygame
import random

pygame.init()


class SeekersGame:
    def __init__(self, local_ai_locations: Iterable[str], config: Config, fps=60):
        self.config = config
        self.fps = fps

        self.players = self.load_local_players(local_ai_locations)
        self.world = World(*self.config.map_dimensions)
        self.goals = []
        self.camps = []
        self.animations = []

    def start(self):
        self.screen = pygame.display.set_mode(self.config.map_dimensions)
        self.clock = pygame.time.Clock()

        random.seed(42)

        # initialize goals
        self.goals = [InternalGoal(get_id("Goal"), self.world.random_position(), Vector(), self.config) for _ in
                      range(self.config.global_goals)]

        # initialize players
        for p in self.players:
            p.seekers = [InternalSeeker(get_id("Seeker"), self.world.random_position(), Vector(), self.config) for _ in
                         range(self.config.global_seekers)]

        # set up camps
        self.camps = self.world.generate_camps(self.players)

        # prepare graphics
        draw.init(self.players)

        self.mainloop()

    def _mainloop(self, thread_pool: ThreadPool):
        ticks = 0

        running = True
        while running:
            # handle pygame events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            # perform game logic
            for _ in range(self.config.updates_per_frame):
                thread_pool.map(
                    lambda player: player.update_ai_action(
                        thread_pool if self.config.global_wait_for_players else False,
                        self.world, self.goals, self.camps, time=ticks
                    ),
                    self.players
                )

                game_logic.tick(self.players, self.camps, self.goals, self.animations, self.world)

                ticks += 1

            # draw graphics
            draw.draw(self.players, self.camps, self.goals, self.animations, self.clock, self.world, self.screen)

            self.clock.tick(self.fps)

            # end game if tournament_length has been reached
            if self.config.global_playtime and ticks > self.config.global_playtime:
                self.print_scores()
                break

    def mainloop(self):
        with ThreadPool(len(self.players)) as thread_pool:
            self._mainloop(thread_pool)

    @staticmethod
    def load_local_players(ais_locations: Iterable[str]) -> list[InternalPlayer]:
        out: list[InternalPlayer] = []

        for location in ais_locations:
            if os.path.isdir(location):
                for filename in glob.glob(os.path.join(location, "ai*.py")):
                    out.append(LocalPlayer.from_file(filename))
            elif os.path.isfile(location):
                out.append(LocalPlayer.from_file(location))
            else:
                raise Exception(f"Invalid AI location: {location!r} is neither a file nor a directory.")

        return out

    def print_scores(self):
        for player in sorted(self.players, key=lambda p: p.score, reverse=True):
            print(f"{player.score} P.:\t{player.name}")
