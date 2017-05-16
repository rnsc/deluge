# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 bendikro <bro.devel+deluge@gmail.com>
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from __future__ import unicode_literals

import json as json_lib
from StringIO import StringIO

import twisted.web.client
from twisted.internet import defer, reactor
from twisted.trial.unittest import SkipTest
from twisted.web.client import Agent, FileBodyProducer
from twisted.web.http_headers import Headers

from deluge.common import utf8_encode_structure

from . import common
from .common import get_test_data_file
from .common_web import WebServerMockBase, WebServerTestBase

common.disable_new_release_check()


class WebServerTestCase(WebServerTestBase, WebServerMockBase):

    @defer.inlineCallbacks
    def test_get_torrent_info(self):

        agent = Agent(reactor)

        self.mock_authentication_ignore(self.deluge_web.auth)
        self.mock_compress_body()

        # This torrent file contains an uncommon field 'filehash' which must be hex
        # encoded to allow dumping the torrent info to json. Otherwise it will fail with:
        # UnicodeDecodeError: 'utf8' codec can't decode byte 0xe5 in position 0: invalid continuation byte
        filename = get_test_data_file('filehash_field.torrent')
        input_file = '{"params": ["%s"], "method": "web.get_torrent_info", "id": 22}' % filename
        headers = {'User-Agent': ['Twisted Web Client Example'],
                   'Content-Type': ['application/json']}
        url = 'http://127.0.0.1:%s/json' % self.webserver_listen_port

        d = yield agent.request(b'POST', url.encode('utf-8'), Headers(utf8_encode_structure(headers)),
                                FileBodyProducer(StringIO(input_file.encode('utf-8'))))
        try:
            body = yield twisted.web.client.readBody(d)
        except AttributeError:
            raise SkipTest('This test requires "t.w.c.readBody()" in Twisted version >= 13.2')

        json = json_lib.loads(body)
        self.assertEqual(None, json['error'])