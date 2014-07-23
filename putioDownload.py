from __future__ import with_statement
import os
import traceback
import putio

from couchpotato.api import addApiView
from couchpotato.core.event import addEvent
from couchpotato.core._base.downloader.main import DownloaderBase
from couchpotato.core.helpers.encoding import sp
from couchpotato.core.helpers.variable import getDownloadDir
from couchpotato.core.logger import CPLog
from couchpotato.environment import Env

log = CPLog(__name__)

autoload = 'Putiodownload'


class Putiodownload(DownloaderBase):

    protocol = ['torrent', 'torrent_magnet']
    status_support = False 

    def __init__(self):
        # Probably a btter way to do this.
        addEvent('download', self._download)
        addEvent('download.enabled', self._isEnabled)
        addEvent('download.enabled_protocols', self.getEnabledProtocol)
        addEvent('download.status', self._getAllDownloadStatus)
        addEvent('download.remove_failed', self._removeFailed)
        addEvent('download.pause', self._pause)
        addEvent('download.process_complete', self._processComplete)
        addApiView('download.%s.test' % self.getName().lower(), self._test)
        addApiView('putiodownload.getfrom', self.getFromPutio, docs = {
            'desc': 'Allows you to download file from prom Put.io',
        })


    def download(self, data = None, media = None, filedata = None):
        if not media: media = {}
        if not data: data = {}
	log.info ('Sending "%s" to put.io', data.get('name'))
	url = data.get('url')
        OAUTH_TOKEN = self.conf('oauth_token')
        client = putio.Client(OAUTH_TOKEN)
        # Need to constuct a the API url a better way.
	client.Transfer.add_url(url,'0','False','http://sabnzbd.dumaresq.ca/couchpotato/api/<api>/putiodownload.getfrom/')
        return True
    
    def test(self):
        OAUTH_TOKEN = self.conf('oauth_token')
        try: 
            client = putio.Client(OAUTH_TOKEN)
            if client.File.list():
                return True
        except:
            log.info('Failed to get file listing, check OAUTH_TOKEN')
            return False

    def getFromPutio(self, **kwargs):
       log.info('Put.io Download has been called')
       OAUTH_TOKEN = self.conf('oauth_token')
       client = putio.Client(OAUTH_TOKEN)
       files = client.File.list()
       # Got to be a better way then a for loop!
       for f in files:
           if str(f.id) == str(kwargs.get('file_id')):
               # Need to read this in from somewhere
               client.File.download(f,'/export/nas/Downloads/')
       return True 
 
config = [{
    'name': 'putiodownload',
    'groups': [
        {
            'tab': 'downloaders',
            'list': 'download_providers',
            'name': 'putiodownload',
            'label': 'put.io Download',
            'description': 'This will start a torrent download on Putio.  <BR>Note:  you must have a putio account and API',
            'wizard': True,
            'options': [
                {
                    'name': 'enabled',
                    'default': 0,
                    'type': 'enabler',
                    'radio_group': 'torrent',
                },
                {
                    'name': 'oauth_token',
                    'label': 'oauth_token',
                    'description': 'This is the OAUTH_TOKEN from your putio API',
                },
#                {
#                    'name': 'callback_URL',
#                    'description': 'This is currently not used',
#                },
                {
                    'name': 'manual',
                    'default': 0,
                    'type': 'bool',
                    'advanced': True,
                    'description': 'Disable this downloader for automated searches, but use it when I manually send a release.',
                },
            ],
        }
    ],
}]
