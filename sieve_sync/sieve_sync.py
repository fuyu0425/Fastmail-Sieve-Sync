#!/usr/bin/env python3
import json
import os
import copy
from typing import Any, Optional

import tomllib
from tap import Tap
from xdg.BaseDirectory import (load_first_config, save_data_path,
                               xdg_config_dirs)

from .sieve import Sieve
from .tiny_jmap_library import TinyJMAPClient

APP_NAME = 'sieve-sync'


class ArgsParser(Tap):
    # FIXME: use xdg as default
    config: Optional[str] = None
    pull: bool = False
    push: bool = False

    def configure(self):
        pass


def main():
    args = ArgsParser().parse_args(known_only=True)
    print(args)
    if args.config:
        with open(args.config, "rb") as f:
            data: Any = tomllib.load(f)
    else:
        config_file: Optional[str] = load_first_config(APP_NAME, "config.toml")
        if not config_file:
            print(
                f"Couldn't find configuration file. Config file must be at: $XDG_CONFIG_HOME/{APP_NAME}/config.toml"
            )
            print("Current value of $XDG_CONFIG_HOME is {}".format(
                os.getenv("XDG_CONFIG_HOME")))
            print("Possible XDG CONFIG DIR", xdg_config_dirs)
            print("Or you can use --config option")
            exit(1)

        with open(config_file, "rb") as f:
            data: Any = tomllib.load(f)
    print(data)

    client = TinyJMAPClient(
        hostname='api.fastmail.com',
        username=data['USERNAME'],
        token=data['TOKEN'],
        cookie=data['COOKIE'],
    )

    sieve = client.get_sieve()

    # insert managed block if not present
    inserted = sieve.insert_sieve_sync_block()

    if inserted:

        set_res = client.set_sieve(sieve)
        print(set_res)
        print('First time running Sieve Sync; added inserted managed block.')
        save_location = data['SAVE_LOCATION']
        with open(save_location, 'w') as f:
            f.write(str(sieve))

        print(f'the rules is saved to {save_location}')
        exit(0)

    if args.pull:

        print('pull from remote')
        save_location = data['SAVE_LOCATION']
        with open(save_location, 'w') as f:
            f.write(str(sieve))

        print(f'updated rules is saved to {save_location}')

    elif args.push:
        save_location = data['SAVE_LOCATION']
        assert os.path.exists(save_location)
        with open(save_location, 'r') as f:
            content = str(f.read())
        old_sieve = copy.deepcopy(sieve)
        new_sieve = Sieve.from_file(content)
        sieve.start = new_sieve.start
        sieve.middle = new_sieve.middle
        sieve.end = new_sieve.end

        print(sieve.start, new_sieve.start, old_sieve.start)

        if sieve != old_sieve:
            set_res = client.set_sieve(sieve)
            print('push to remote')
            with open(save_location, 'w') as f:
                f.write(str(sieve))
        else:
            print('no change so far; skip pushing')


if __name__ == '__main__':
    main()
