from .seekers_types import *
from . import game_logic, draw

import collections
import typing
import os
import glob
import pygame
import random

pygame.init()


class GameFullError(Exception): ...


class SeekersGame:
    def __init__(self, local_ai_locations: typing.Iterable[str], config: Config, fps=120):
        self.config = config
        self.fps = fps

        self.players = self.load_local_players(local_ai_locations)
        self.world = World(*self.config.map_dimensions)
        self.goals = []
        self.camps = []
        self.animations = []
        self.ticks = 0

    def start(self):
        self.screen = pygame.display.set_mode(self.config.map_dimensions)
        self.clock = pygame.time.Clock()

        random.seed(42)

        # initialize goals
        self.goals = [InternalGoal(get_id("Goal"), self.world.random_position(), Vector(), self.config) for _ in
                      range(self.config.global_goals)]

        # initialize players
        for p in self.players.values():
            p.seekers = {
                (id_ := get_id("Seeker")): InternalSeeker(id_, self.world.random_position(), Vector(), p, self.config)
                for _ in range(self.config.global_seekers)
            }

        # set up camps
        self.camps = self.world.generate_camps(self.players.values())

        # prepare graphics
        draw.init(self.players.values())

        self.mainloop()

    def _mainloop(self, thread_pool: ThreadPool):
        running = True

        while running:
            # handle pygame events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            # perform game logic
            for _ in range(self.config.updates_per_frame):
                for player in self.players.values():
                    player.poll_ai(
                        "wait" if self.config.global_wait_for_players else thread_pool, self.world, self.goals,
                        self.players, self.ticks
                    )

                game_logic.tick(self.players.values(), self.camps, self.goals, self.animations, self.world)

                self.ticks += 1

            # draw graphics
            draw.draw(self.players.values(), self.camps, self.goals, self.animations, self.clock, self.world,
                      self.screen)

            self.clock.tick(self.fps)

            # end game if tournament_length has been reached
            if self.config.global_playtime and self.ticks > self.config.global_playtime:
                self.print_scores()
                break

    def mainloop(self):
        # TODO: Add grpc server support
        # TODO: Add wait for all players to join

        with ThreadPool(len(self.players)) as thread_pool:
            self._mainloop(thread_pool)

    @staticmethod
    def load_local_players(ai_locations: typing.Iterable[str]) -> dict[str, InternalPlayer]:
        out: dict[str, InternalPlayer] = {}

        for location in ai_locations:
            if os.path.isdir(location):
                for filename in glob.glob(os.path.join(location, "ai*.py")):
                    player = LocalPlayer.from_file(filename)
                    out |= {player.id: player}
            elif os.path.isfile(location):
                player = LocalPlayer.from_file(location)
                out |= {player.id: player}
            else:
                raise Exception(f"Invalid AI location: {location!r} is neither a file nor a directory.")

        return out

    def add_player(self, player: InternalPlayer):
        if len(self.players) >= self.config.global_players:
            raise GameFullError(
                f"Game full. Cannot add more players. Max player count is {self.config.global_players}."
            )

        self.players |= {player.id: player}

    def print_scores(self):
        for player in sorted(self.players.values(), key=lambda p: p.score, reverse=True):
            print(f"{player.score} P.:\t{player.name}")

    @property
    def seekers(self):
        return collections.ChainMap(*(p.seekers for p in self.players.values()))
