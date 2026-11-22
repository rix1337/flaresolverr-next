"""Persistent diagnostics for HTTP 500 responses, without request contents."""

import logging
import os
from logging.handlers import RotatingFileHandler

_logger = logging.getLogger('flaresolverr.http_errors')
_logger.propagate = False
_logger.addHandler(logging.NullHandler())

_COMMANDS = ('request.get', 'request.post', 'sessions.create', 'sessions.list', 'sessions.destroy')


def configure_error_log():
    default_directory = '/config' if os.path.isdir('/config') else '.'
    path = os.environ.get('ERROR_LOG_FILE', os.path.join(default_directory, 'flaresolverr-errors.log'))
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=1024 * 1024, backupCount=3, encoding='utf-8')
    except OSError:
        logging.warning('Could not open the HTTP 500 error log')
        return
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%dT%H:%M:%S'))
    _logger.setLevel(logging.ERROR)
    _logger.addHandler(handler)


def record_http_error(version, stage, error, cmd=None, elapsed_ms=None):
    cause = error.__cause__ or error.__context__ or error
    trace = cause.__traceback__
    while trace and trace.tb_next:
        trace = trace.tb_next
    location = 'unknown'
    if trace:
        code = trace.tb_frame.f_code
        location = f'{os.path.basename(code.co_filename)}:{trace.tb_lineno}:{code.co_name}'
    _logger.error(
        'v%s HTTP 500 stage=%s command=%s exception=%s elapsed_ms=%s location=%s',
        version, stage, cmd if cmd in _COMMANDS else 'unknown', type(cause).__name__, elapsed_ms, location,
    )
