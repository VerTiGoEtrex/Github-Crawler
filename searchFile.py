#!/usr/bin/env python

import sys
import re
import urllib2
import sqlite3

def downloadURL(url):
    r = urllib2.urlopen(url)
    return r.read()

def isSSLKey(text):
    privateKeyRE = re.compile(r'-----BEGIN (RSA )?PRIVATE KEY-----\n([0-9A-Za-z=+/\n]{100,})-----END (RSA )?PRIVATE KEY-----')
    return re.match(privateKeyRE, text) is not None

def isBitcoin(url):
    return url.find("wallet.dat") >= 0

def extractAWSKeys(text):
    keys = []

    keynameRE = re.compile(r'(AKA)')
    keyRE = re.compile(r'([^0-9A-Za-z+/]|^)([0-9A-Za-z=+/]{40})([^0-9A-Za-z=+/]|$)')

    if re.search(keynameRE, text):
        keys += [m[1] for m in re.findall(keyRE, text)]
    return keys

def findSecrets(url, dbc):
    text = downloadURL(url)

    # Check for various kinds of secrets and save to NoSQL
    keys = extractAWSKeys(text)
    if keys:
        dbc.execute('INSERT INTO Secrets VALUES("");')

def main():
    fileName = raw_input("file name: ")
    with open(fileName, 'r') as f:
        s = f.read()
        if re.match(privateKeyRE, s):
            print "Match!"
        else:
            print "Not a match..."

if __name__=='__main__':
    main()
