from multiprocessing import Process
import argparse
import os.path
import sys
import logging
from collections import defaultdict

import seekers.grpc



def main():
    parser = argparse.ArgumentParser(description='Run python seekers AIs as gRPC clients.')
    parser.add_argument("-address", "-a", type=str, default="localhost:7777",
                        help="Address of the server. (default: localhost:7777)")
    parser.add_argument("-loglevel", "-log", "-l", type=str, default="ERROR",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("ai_files", type=str, nargs="+", help="Paths to the AIs.")

    args = parser.parse_args()

    _AIS = defaultdict(int)

    def ai_name(filepath: str) -> str:
        name, _ = os.path.splitext(os.path.basename(filepath))

        _AIS[name] += 1

        if _AIS[name] > 1:
            name += f"_{_AIS[name]}"

        return name

    processes = []

    for arg in args.ai_files:
        name = ai_name(arg)

        def run_ai(filepath: str, name: str):
            with open(filepath) as f:
                mod = compile(f.read(), os.path.abspath(arg), "exec")

            mod_dict = {}
            exec(mod, mod_dict)
            decide = mod_dict["decide"]

            logging.basicConfig(level=args.loglevel, style="{", format=f"[{name.ljust(18)}] {{levelname}}: {{message}}", stream=sys.stdout)

            seekers.grpc.GrpcSeekersClient(name, decide, args.address).mainloop()

        processes.append(
            Process(
                target=run_ai,
                args=(arg, name),
                daemon=True,
                name=f"AI {name!r}"
            )
        )

    for process in processes:
        process.start()

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
