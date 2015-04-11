#!/usr/bin/env python
# encoding: utf-8

from github3 import login # pip install github3.py
import github3
import re
import logging
import inspect
import time

# CONFIG
fileHandler = logging.FileHandler('slurp.log')
SLEEPTIME = 10 # seconds
with open('AUTH', 'r') as f:
    TOKEN = f.read(40)
assert(len(TOKEN) == 40)
DEBUGLOGGING = False
# /CONFIG

def handleCommitFile(repo=None, fileObj=None):
    #TODO Fill this in, Daniel
    print 'Daniel\'s function to parse file objects'

def getRateLimit(gh):
    return gh.rate_limit()['resources']['core']['remaining']

class EventGetter():
    def __init__(self, gh):
        self.lastId = 0
        self.gh = gh
        self.eventIter = self.gh.iter_events()
        self.numEvents = 0
        self.numPushEvents = 0

    def getNewPushEvents(self):
        self.eventIter.refresh(True)
        newEvents = list()
        newLastId = self.lastId
        for e in self.eventIter:
            if e.id <= self.lastId:
                break
            newLastId = max(newLastId, e.id)
            self.numEvents += 1
            if e.type == 'PushEvent':
                newEvents.append(e)
        self.numPushEvents += len(newEvents)
        self.lastId = newLastId
        return newEvents

    def printStats(self):
        print '[*] EventGetter -- numEvents: {}, numPushEvents: {}, Ratio: {}'.format(self.numEvents, self.numPushEvents, float(self.numPushEvents)/self.numEvents)

class EventCommitGetter():
    def __init__(self, gh):
        self.gh = gh
        self.shaSet = set()
        self.numSkipped = 0
        self.numReturned = 0

    def getNewCommits(self, event):
        assert event.type == 'PushEvent'
        newCommits = list()
        for commit in event.payload['commits']:
            commitSha = commit['sha']
            if commitSha in self.shaSet:
                self.numSkipped += 1
                continue
            self.shaSet.add(commitSha)
            # This is some hackery to avoid consuming our ratelimit when we don't need to
            repoObj = dict()
            repoObj['url'] = 'https://api.github.com/repos/{group}/{repo}'.format(group=event.repo[0], repo = event.repo[1])
            repo = github3.repos.repo.Repository(repoObj, session=self.gh)
            c = repo.commit(commitSha)
            # Get the commit, and send the files off to Daniel
            newCommits.append((event.repo, c))
        self.numReturned += len(newCommits)
        return newCommits

    def printStats(self):
        print '[*] EventCommitGetter -- numCommits: {}, numSkipped: {}, len(shaSet): {}'.format(self.numReturned, self.numSkipped, len(self.shaSet))

class CommitFileGetter():
    def __init__(self, gh):
        self.gh = gh
        self.shaSet = set()
        self.numSkipped = 0
        self.numReturned = 0

    def getNewFiles(self, commit):
        newFiles = list()
        for f in commit[1].files:
            fileSha = f['sha']
            if fileSha in self.shaSet:
                self.numSkipped += 1
                continue
            self.shaSet.add(fileSha)
            newFiles.append((commit[0], f))
        self.numReturned += len(newFiles)
        return newFiles

    def printStats(self):
        print '[*] CommitFileGetter -- numFiles: {}, numSkipped: {}, len(shaSet): {}'.format(self.numReturned, self.numSkipped, len(self.shaSet))

def main():
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    logger = logging.getLogger('github3')
    logger.addHandler(fileHandler)
    if DEBUGLOGGING:
        logger.addHandler(streamHandler) # Print debug output to stderr
    logger.setLevel(logging.DEBUG)

    gh = login(token=TOKEN)

    eventGetter = EventGetter(gh)
    commitGetter = EventCommitGetter(gh)
    fileGetter = CommitFileGetter(gh)
    while True:
        try:
            initialRateLimit = getRateLimit(gh)
            print '[-] Starting with {} requests'.format(initialRateLimit)
            print '[+] Getting events!'.format()
            pullEvents = eventGetter.getNewPushEvents()
            print '[+] Getting commits!'.format()
            allCommits = list()
            for event in pullEvents:
                commits = commitGetter.getNewCommits(event)
                allCommits.extend(commits)
            print '[+] Getting files!'.format()
            allFiles = list()
            for commit in allCommits:
                files = fileGetter.getNewFiles(commit)
                allFiles.extend(files)
            print '[+] Sending file objects to secret finder'.format()
            for f in allFiles:
                handleCommitFile(repo=f[0], fileObj=f[1])
            endRateLimit = getRateLimit(gh)
            print '[+] NEW: {} events, {} commits, {} files'.format(len(pullEvents), len(allCommits), len(allFiles))
            print '[+] Sleeping for {} seconds with {} requests remaining -- used {} requests'.format(SLEEPTIME, endRateLimit, max(0, initialRateLimit - endRateLimit))
            eventGetter.printStats()
            commitGetter.printStats()
            fileGetter.printStats()
            # wait SLEEPING seconds... TODO: Make this adaptive (ratelimit_remaining, time before ratelimit reset, and average requests per minute or something)
            #return #FIXME this is just for debugging
            time.sleep(SLEEPTIME)
        except KeyboardInterrupt:
            print '[*] EXITING'
            eventGetter.printStats()
            commitGetter.printStats()
            fileGetter.printStats()
            raise
        except Exception, e:
            print '[X] Got an exception! Sleeping for {} seconds'.format(SLEEPTIME)
            print e
            time.sleep(SLEEPTIME)

if __name__ == '__main__':
    main()
