
from logging import getLogger
from typing import Any
from pprint import pformat

from phabricator import Phabricator

logger = getLogger(__name__)


class DiffHest:
    def __init__(self, phab: Phabricator):
        self.phab = phab


    def process(self, j: dict[str, Any]) -> None:
        logger.info('\n'+pformat(j))
        o = j.get('object')
        if not o:
            logger.error('no "object" key in json')
            return

        t = o.get('type')
        if t != 'DREV':
            logger.warning(f'can work only with object type DREV, got {t} instead')
            return

        p = o.get('phid')
        logger.info(f'querying phabricator for revision {p}')
        query = self.phab.differential.revision.search(constraints=dict(phids=[p])).data
        if not query:
            logger.error('no revision found')
            return
        revision = query[0]
        logger.info('\n'+pformat(revision)+'\n'+'-'*10+'\n')
