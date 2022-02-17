
from logging import getLogger
from typing import Any, Optional
from pprint import pformat
import re

from phabricator import Phabricator

RE_TICKET = re.compile(r'^T(\d+):')
logger = getLogger(__name__)


class DiffHest:
    def __init__(self, phab: Phabricator):
        self.phab = phab
        h = phab.host.rstrip('/')
        if h.endswith('/api'):
            h = h[:-len('/api')]
        self.phab_host = h


    def process(self, payload: dict[str, Any]) -> None:
        logger.info(f'\n\n{"="*10}\n\n')
        revision = self.get_revision_from_request(payload)
        if not revision:
            return

        rid = revision["id"]
        logger.info(f'Working with revision {self.phab_host}/D{rid} :\n{pformat(revision["fields"])}\n{"- "*5}')
        task_phid = self.get_task_from_revision(revision)
        if not task_phid:
            return

        self.link_revision_to_task(revision, task_phid)
        print(f'D{rid}: linked\n')


    def get_revision_from_request(self, req: dict[str, Any]) -> dict[str, Any]:
        obj = req.get('object')
        if not obj:
            logger.error(f'no "object" key in request:\n{pformat(req)}')
            return

        obj_type = obj.get('type')
        if obj_type != 'DREV':
            logger.warning(f'can work only with object type DREV, got {obj_type} instead; ignoring')
            return

        revision_phid = obj.get('phid')

        tps = [x['phid'] for x in req.get('transactions')]
        if not tps:
            logger.error(f'no transaction phids presents in request; ignoring:\n{pformat(req)}')
            return

        # logger.info(f'querying phabricator for transactions in revision {revision_phid}')
        # transactions = self.phab.transaction.search(
        #     objectIdentifier=revision_phid,
        #     constraints=dict(phids=tps)
        # ).data
        # if not transactions:
        #     logger.error('no transactions found in phabricator; ignoring')
        #     return
        # if not any(x for x in transactions if x['type'] == 'create'):
        #     logger.info('no "create" transactions in request; ignoring')
        #     return

        logger.info(f'querying phabricator for revision {revision_phid}')
        query = self.phab.differential.revision.search(constraints=dict(phids=[revision_phid])).data
        if not query:
            logger.error('no revision found')
            return
        return query[0]


    def get_task_from_revision(self, revision: dict[str, Any]) -> Optional[str]:
        match = RE_TICKET.search(revision['fields']['title'])
        if not match:
            logger.info('no T### in revision title')
            return
        task_id = int(match.group(1))
        logger.info(f'querying for T{task_id}')
        query = self.phab.maniphest.search(constraints=dict(ids=[task_id])).data
        if not query:
            logger.info(f'no such task found (typo or access denied)')
            return
        return query[0]['phid']

    def link_revision_to_task(self, revision: dict[str, Any], task_phid: str) -> None:
        rev_phid = revision['phid']
        logger.info(f'linking revision {rev_phid} to task {task_phid}')
        self.phab.differential.revision.edit(
            objectIdentifier=rev_phid,
            transactions=[dict(
                type='tasks.add',
                value=[task_phid]
            )]
        )
