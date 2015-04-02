#!/usr/bin/env python
# encoding: utf-8

from github3 import login # pip install github3.py
import re
import logging
import inspect
import time

# CONFIG
fileHandler = logging.FileHandler('slurp.log')
SLEEPTIME = 60 # seconds
CLEARITERS = 50 # Amount of iters before clearing the sha set for space
with open('AUTH', 'r') as f:
    TOKEN = f.read(40)
assert(len(TOKEN) == 40)
# /CONFIG


def handleCommitFile(fileObj=None):
    print 'Daniel\'s function to parse file objects'

streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger = logging.getLogger('github3')
logger.addHandler(fileHandler)
#logger.addHandler(streamHandler) # Uncomment this line to print debugging information to stderr
logger.setLevel(logging.DEBUG)

gh = login(token=TOKEN)

# print inspect.getmembers(gh)

eventETag = None

startRequestLimit = gh.rate_limit()['resources']['core']['remaining']
print '[-] Starting with {} requests'.format(startRequestLimit)
commitShaSet = set()
fileShaSet = set()

iters = 0
while iters < 4: #FIXME: Set this back to True
    # Main event loop
    if iters % CLEARITERS == 0:
        commitShaSet = set()
        fileShaSet = set()
    numEvents = 0
    numPushEvents = 0
    numCommits = 0
    numFiles = 0
    print '[+] Getting events!'.format()
    events = gh.iter_events(etag=eventETag)
    for e in events:
        numEvents += 1
        if e.type == 'PushEvent':
            # Get those commits :)
            loadedRepo = False
            repo = None
            for commit in e.payload['commits']:
                if commit['sha'] not in commitShaSet:
                    commitShaSet.add(commit['sha'])
                    if not loadedRepo:
                        repo = gh.repository(*e.repo)
                        if repo is None:
                            break
                        loadedRepo = True
                    numCommits += 1
                    # Get the commit, and send the files off to Daniel
                    c = repo.commit(commit['sha'])
                    for f in c.files:
                        if f['sha'] not in fileShaSet:
                            fileShaSet.add(f['sha'])
                            handleCommitFile(f)
                        else:
                            print 'Skipped a file because of SHA set'
                else:
                    print 'Skipped a commit because of SHA set'
            numPushEvents += 1
    print '[+] Finished parsing events ({} PushEvent out of {} total events -- ratio {})'.format(numPushEvents, numEvents, float(numPushEvents)/numEvents)
    eventETag = events.etag
    print '[+] Sleeping for {} seconds with {} requests remaining'.format(SLEEPTIME, events.ratelimit_remaining)
    # wait SLEEPING seconds... TODO: Make this adaptive (ratelimit_remaining, time before ratelimit reset, and average requests per minute or something)
    time.sleep(SLEEPTIME)
    iters += 1
finishRequestLimit = gh.rate_limit()['resources']['core']['remaining']
print '[-] Finished with {} requests remaining, used {} requests'.format(finishRequestLimit, startRequestLimit - finishRequestLimit)
