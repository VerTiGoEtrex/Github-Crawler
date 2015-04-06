#!/usr/bin/env python

import pycurl
import sys
import re
import urllib2

class CurlSaver:
    def __init__(self):
        self.data = ''
    def writeFn(self, buf):
        self.data += buf

def downloadURL(url):
    #ret = ''
    #try:
    #    cs = CurlSaver()
    #    c = pycurl.Curl()
    #    c.setopt(c.URL, url)
    #    c.setopt(c.WRITEFUNCTION, cs.writeFn)
    #    c.perform()
    #    c.close()
    #    ret = cs.data
    #except:
    #    pass

    #return cs.data

    r = urllib2.urlopen(url)
    return r.read()

def extractAWSKeys(text):
    keys = []

    awsRE = re.compile('aws', re.IGNORECASE)
    keyRE = re.compile(r'([^0-9A-Za-z=+]|^)([0-9A-Za-z=+]{40})([^0-9A-Za-z=+]|$)')

    if re.search(awsRE, text):
        keys += [m[1] for m in re.findall(keyRE, text)]

    return keys


def getKeysFromURL(url):
    text = downloadURL(url)
    keys = extractAWSKeys(text)
    return (text, keys)

def main():
    keyResults = [getKeysFromURL(url) for url in sys.stdin]
    
    for text, keys in keyResults:
        print repr(keys)

if __name__=='__main__':
    main()
