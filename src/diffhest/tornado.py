import hashlib
import hmac
import json
from logging import getLogger
from typing import Optional

from tornado.httputil import HTTPHeaders
import tornado.ioloop
import tornado.web as tw

from . import DiffHest

logger = getLogger(__name__)


class PhabReciever(tw.RequestHandler):
    def initialize(self, dh: DiffHest, hmac: str) -> None:
        self.interactor = dh
        self.hmac = hmac


    def validate_request(self, body: bytes, headers: HTTPHeaders) -> Optional[str]:
        if not headers.get('Content-Type') == 'application/json':
            m = 'not a json'
            logger.info(m)
            return m

        if not self.hmac:
            return None

        signature_sent = headers.get('X-Phabricator-Webhook-Signature')
        if not signature_sent:
            m = 'no phabricator signature header'
            logger.info(m)
            return m

        signature_calculated = hmac.new(
            self.hmac.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()

        if signature_calculated != signature_sent:
            m = f'phabricator signature mismatch; in header: {signature_sent}, calculated: {signature_calculated}'
            logger.info(m)
            return m

        return None

    def post(self) -> None:
        try:
            logger.debug('POST!\nbody: %s\nheaders: %s', self.request.body, self.request.headers)
            vmsg = self.validate_request(self.request.body, self.request.headers)
            if vmsg:
                self.set_status(400, vmsg)
                self.finish()
                return

            msg = json.loads(self.request.body)
            self.interactor.process(msg)

        except Exception as e:
            logger.error(e)
            self.set_status(500, f'Some internal server error: {e}')
            self.finish()


class TornadoServer(tw.Application):
    def __init__(self, port: int, dh: DiffHest, hmac: str):
        super().__init__([
            tw.url('/', tw.RequestHandler),
            tw.url('/post', PhabReciever, dict(
                dh=dh,
                hmac=hmac
            ))
        ])
        self.port = port
        logger.info(f'Tornado app created @ port {self.port}')

    def run(self) -> None:
        self.listen(self.port)
        logger.info('Tornado serving forever')
        tornado.ioloop.IOLoop.instance().start()
