import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import error_log
import flaresolverr_service
from bottle_plugins.error_plugin import error_plugin
from dtos import V1RequestBase


class ErrorLogTests(unittest.TestCase):
    def test_http_500_paths_write_diagnostics_without_private_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'errors.log'
            with patch.dict(os.environ, {'ERROR_LOG_FILE': str(path)}):
                error_log.configure_error_log()
            handler = error_log._logger.handlers[-1]
            self.addCleanup(error_log._logger.removeHandler, handler)
            try:
                with patch('flaresolverr_service._controller_v1_handler',
                           side_effect=TimeoutError('https://source.invalid/private?token=secret')):
                    with self.assertLogs(level=logging.ERROR):
                        result = flaresolverr_service.controller_v1_endpoint(
                            V1RequestBase({'cmd': 'request.get'}))
                self.assertTrue(result.__error_500__)

                @error_plugin
                def route():
                    raise ValueError('private request body')

                with self.assertLogs(level=logging.ERROR):
                    route()
                lines = path.read_text().splitlines()
                self.assertEqual(2, len(lines))
                self.assertIn('HTTP 500 stage=command command=request.get exception=TimeoutError', lines[0])
                self.assertIn('HTTP 500 stage=route command=unknown exception=ValueError', lines[1])
                for private in ('source.invalid', 'secret', 'private request body'):
                    self.assertNotIn(private, '\n'.join(lines))
            finally:
                handler.close()
