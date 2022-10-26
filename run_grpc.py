import argparse
import os.path
from collections import defaultdict
from multiprocessing import Process

import seekers.grpc


def main():
    parser = argparse.ArgumentParser(description='Run seekers AIs as clients.')
    parser.add_argument("-address", "-a", type=str, default="localhost:7777",
                        help="Address of the server. (default: localhost:7777)")
    parser.add_argument("-loglevel", "-log", "-l", type=str, default="ERROR")
    parser.add_argument("ai_files", type=str, nargs="+", help="Paths to the ais.")

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
        with open(arg) as f:
            mod = compile(f.read(), os.path.abspath(arg), "exec")

        name = ai_name(arg)

        mod_dict = {}
        exec(mod, mod_dict)
        decide = mod_dict["decide"]

        def run_ai():
            seekers.grpc.GrpcSeekersClient(name, decide, args.address).mainloop()

        processes.append(
            Process(
                target=run_ai,
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
