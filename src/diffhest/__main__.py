#!/usr/bin/env python3

import argparse
import os
import logging
from logging import getLogger
from typing import Any, NamedTuple

from phabricator import Phabricator

from diffhest import DiffHest
from diffhest.tornado import TornadoServer

class Args(NamedTuple):
    phabricator: str
    phabricator_token: str
    phabricator_hmac: str
    port: int
    log_notime: bool


def parse_args() -> Args:
    class EnvDefault(argparse.Action):
        def __init__(self, envvar: str, required: bool=True, default: Any=None, **kwargs: Any):
            if envvar in os.environ:
                default = os.environ[envvar]
            if required and default:
                required = False
            super().__init__(default=default, required=required, **kwargs)

        def __call__(self, parser: Any, namespace: Any, values: Any, option_string: Any=None) -> None:
            setattr(namespace, self.dest, values)


    p = argparse.ArgumentParser()
    p.add_argument('--phabricator', action=EnvDefault, envvar='DIFFHEST_PHABRICATOR_URL', required=False)
    p.add_argument('--phabricator_token', action=EnvDefault, envvar='DIFFHEST_PHABRICATOR_TOKEN', required=False)
    p.add_argument('--phabricator_hmac', action=EnvDefault, envvar='DIFFHEST_PHABRICATOR_HMAC')
    p.add_argument('--port', action=EnvDefault, envvar='DIFFHEST_PORT', type=int)
    p.add_argument('--log_notime', action='store_true')
    return Args(**p.parse_args().__dict__)


logger = getLogger(__name__)



def main() -> None:
    args = parse_args()

    fmt = '%(name)s - %(levelname)s - %(message)s'
    if not args.log_notime:
        fmt = '%(asctime)s - '+fmt
    logging.basicConfig(format=fmt, level=logging.INFO)


    phab = Phabricator(host=args.phabricator, token=args.phabricator_token)
    logger.info('updating phabricator interfaces...')
    phab.update_interfaces()
    logger.info(f'working with {phab.host}')

    interactor = DiffHest(phab)

    ws = TornadoServer(args.port, interactor, args.phabricator_hmac)
    ws.run()


if __name__ == "__main__":
    main()
