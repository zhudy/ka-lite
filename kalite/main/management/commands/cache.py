import time
import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from kalite.main.models import VideoFile
from kalite.utils.videos import download_video, DownloadCancelled
from utils.jobs import force_job
from utils import caching
from kalite.main import topicdata
        

class Command(BaseCommand):
    help = "Manipulate the cache (create, show, clear)"
    
    def handle(self, *args, **options):
        cmd = sys.argv[2]
        if cmd in ["create", "recreate", "refresh"]:
            self.create_cache(force=(cmd in ["recreate", "refresh"]))
        elif cmd in ["show", "check"]:
            self.show_cache()
        elif cmd in ["clear", "delete"]:
            self.clear_cache()
        else:
            raise NotImplementedError("Unknown option: %s" % cmd)
        
        
        

    def create_cache(self, force=False, path=None):
        """Go through each cacheable page, and either:
        (a) Cache each page that is not
        or
        (b) Kill and regenerate each page"""

        # Base case
        if path:
            if force:
                if caching.has_cache_key(path=path):
                    caching.expire_page(path=path)
                    print "[Redo]\t%s" % path
                else:
                    print "[Miss]\t%s" % path
                caching.create_cache(path=path)
                    
            else:
                if not caching.has_cache_key(path=path):
                    caching.create_cache(path=path)
                    print "[Miss]\t%s" % path
                
            if not caching.has_cache_key(path=path):
                # should never get here!
                print "%s%s" % ("?"*10, path)
        
        # Recursive call
        else:
            for type in ['Video', 'Exercise', 'Topic']:
                print "Generating %ss:" % type
                for n in topicdata.NODE_CACHE[type].values():
                    self.create_cache(path=n['path'])
                
                
    def show_cache(self, path=None):
        """Go through each cacheable page, and show which are cached and which are NOT"""
        
        # Base case
        if path:
            if caching.has_cache_key(path=path):
                print "\t%s" % path
        
        else:
            for type in ['Video', 'Exercise', 'Topic']:
                print "Cached %ss:" % type
                for n in topicdata.NODE_CACHE[type].values():
                    self.show_cache(path=n['path'])

                
    def clear_cache(self, path=None):
        """Go through each cacheable page, and show which are cached and which are NOT"""
        
        # Base case
        if path:
            if caching.has_cache_key(path=path):
                print "\t%s" % path
                caching.expire_page(path=path)
            else:
                print "skipping %s" % path
        else:
            for type in ['Video', 'Exercise', 'Topic']:
                print "Clearing %ss:" % type
                for n in topicdata.NODE_CACHE[type].values():
                    self.clear_cache(path=n['path'])
                