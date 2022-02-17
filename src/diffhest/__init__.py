
from logging import getLogger
from typing import Any, Optional
from pprint import pformat

from phabricator import Phabricator

logger = getLogger(__name__)


class DiffHest:
    def __init__(self, phab: Phabricator):
        self.phab = phab
        h = phab.host.rstrip('/')
        if h.endswith('/api'):
            h = h[:-len('/api')]
        self.phab_host = h


    def process(self, payload: dict[str, Any]) -> None:
        revision = self.get_revision_from_request(payload)
        if not revision:
            return

        rid = revision["id"]
        logger.info(f'\nWorking with revision {self.phab_host}/D{rid} :\n{pformat(revision)}\n{"- "*5}\n')
        task_id = self.get_task_from_revision(revision)
        if not task_id:
            return

        self.link_revision_to_task(revision, task_id)
        print(f'D{rid}: processed\n{"="*10}\n')


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
        if revision_phid in self.ignored_phids:
            logger.info(f'revision {revision_phid} is ignored')
            return

        tps = [x['phid'] for x in req.get('transactions')]
        if not tps:
            logger.error(f'no transaction phids presents in request; ignoring:\n{pformat(req)}')
            return

        logger.info(f'querying phabricator for transactions in revision {revision_phid}')
        transactions = self.phab.transaction.search(
            objectIdentifier=revision_phid,
            constraints=dict(phids=tps)
        ).data
        if not transactions:
            logger.error('no transactions found in phabricator; ignoring')
            return

        if not any(x for x in transactions if x['type'] == 'create'):
            logger.info('no "create" transactions in request; ignoring')
            return

        logger.info(f'querying phabricator for revision {revision_phid}')
        query = self.phab.differential.revision.search(constraints=dict(phids=[revision_phid])).data
        if not query:
            logger.error('no revision found')
            return


    def get_task_from_revision(revision: dict[str, Any]) -> Optional[int]:
        logger.info('get task: not implemented')
        return None


    def link_revision_to_task(revision: dict[str, Any], task_id: int) -> None:
        logger.info('link: not implemented')
