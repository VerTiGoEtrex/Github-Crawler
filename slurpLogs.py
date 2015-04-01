#!/usr/bin/env python
# encoding: utf-8

from github import Github
import re

# CONFIG
with open('AUTH', 'r') as f:
    TOKEN = f.read(40)
assert(len(TOKEN) == 40)

b = Github(TOKEN)
