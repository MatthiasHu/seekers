from .seekers_types import *
from . import game_logic, draw

from typing import Iterable
import os
import glob
import traceback
import pygame
import sys
import copy
import random

pygame.init()


class SeekersGame:
    def __init__(self, ais_locations: Iterable[str] = ("./ais",), num_goals=5, num_seekers=5, dimensions=(768, 768),
                 tournament_length: int | None = 16384, updates_per_frame: int = 1,
                 fps=60):
        self.num_goals = num_goals
        self.num_seekers = num_seekers
        self.tournament_length = tournament_length
        self.updates_per_frame = updates_per_frame
        self.fps = fps

        self.world = World(*dimensions)
        self.goals = []
        self.players = self.load_players(ais_locations)
        self.camps = []
        self.animations = {"score": []}

    @property
    def dimensions(self):
        return self.world.width, self.world.height

    def start(self):
        self.screen = pygame.display.set_mode(self.dimensions)
        self.clock = pygame.time.Clock()

        random.seed(42)

        # initialize goals
        self.goals = [Goal(self.world.random_position()) for _ in range(self.num_goals)]

        # initialize players
        for p in self.players:
            p.seekers = [Seeker(self.world.random_position()) for _ in range(self.num_seekers)]

        # set up camps
        self.camps = self.world.generate_camps(self.players)

        # prepare graphics
        draw.init(self.players)

        self.mainloop()

    def mainloop(self):
        frame = 0
        running = True

        while running:
            # handle pygame events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            # perform game logic
            for _ in range(self.updates_per_frame):
                self.call_ais()

                game_logic.tick(self.players, self.camps, self.goals, self.animations, self.world)

                frame += 1

            # draw graphics
            draw.draw(self.players, self.camps, self.goals, self.animations, self.clock, self.world, self.screen)

            self.clock.tick(self.fps)

            # end game if tournament_length has been reached
            if self.tournament_length and frame > self.tournament_length:
                self.print_scores()
                running = False

    def load_players(self, ais_locations: Iterable[str]) -> list[Player]:
        out: list[Player] = []

        for location in ais_locations:
            if os.path.isdir(location):
                for filename in glob.glob(os.path.join(location, "ai*.py")):
                    out.append(self.load_player(filename))
            elif os.path.isfile(location):
                out.append(self.load_player(location))
            else:
                raise Exception(f"Invalid AI location: {location!r} is neither a file nor a directory.")

        return out

    def load_player(self, filepath: str) -> Player:
        name, _ = os.path.splitext(filepath)

        p = Player(name, ai=self.load_ai(filepath))

        return p

    @staticmethod
    def load_ai(filepath: str) -> PlayerAI:
        try:
            with open(filepath) as f:
                code = f.read()
            mod = compile(code, filepath, "exec")

            try:
                mod_dict = {}
                exec(mod, mod_dict)

                ai = mod_dict["decide"]
            except Exception as e:
                raise Exception(f"AI {filepath!r} does not have a 'decide' function") from e

            return PlayerAI(filepath, os.path.getctime(filepath), ai)
        except Exception:
            print(f"Error while loading AI {filepath!r}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print(file=sys.stderr)

    def call_ais(self):
        for player, camp in zip(self.players, self.camps):
            # reload ai if its file has changed
            if os.path.getctime(player.ai.filepath) > player.ai.timestamp:
                player.ai = self.load_ai(player.ai.filepath)

            self.call_ai(player, camp)

    def get_ai_input(self, player: Player) \
            -> tuple[list[Seeker], list[Seeker], list[Seeker], list[Goal], list[Player], list[Camp], World]:
        all_players = copy.deepcopy(self.players)

        player_i = self.players.index(player)
        this_player = all_players[player_i]

        other_players = [player for player in all_players if player != this_player]

        all_seekers = [seeker for player in all_players for seeker in player.seekers]
        other_seekers = [seeker for player in other_players for seeker in player.seekers]

        return (
            this_player.seekers,
            other_seekers,
            all_seekers,
            copy.deepcopy(self.goals),
            other_players,
            copy.deepcopy(self.camps),
            copy.deepcopy(self.world)
        )

    def call_ai(self, player: Player, camp: Camp):
        def warn_invalid_data():
            print(f"The AI of Player {player.name} returned invalid data.")

        own_seekers, other_seekers, all_seekers, goals, other_players, camps, world = self.get_ai_input(player)

        try:
            new_seekers = player.ai.decide_function(own_seekers, other_seekers, all_seekers, goals, other_players, camp, camps, world)
        except Exception:
            print(f"The AI of Player {player.name} raised an exception:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

            new_seekers = []

        if isinstance(new_seekers, list):
            for new, original in zip(new_seekers, player.seekers):
                if isinstance(new, Seeker):
                    status = Seeker.copy_alterables(new, original)
                    if not status: warn_invalid_data()
                else:
                    warn_invalid_data()
        else:
            warn_invalid_data()

    def print_scores(self):
        for player in sorted(self.players, key=lambda p: p.score, reverse=True):
            print(f"{player.score} P.:\t{player.name}")
