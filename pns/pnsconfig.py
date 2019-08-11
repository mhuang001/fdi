# -*- coding: utf-8 -*-
from os.path import join


# base url for webserver
pnsconfig = dict(baseurl='/v0.5')

# username, passwd, flask ip, flask port
pnsconfig['node'] = {'username': 'foo', 'password': 'bar',
                     'host': '0.0.0.0', 'port': 5000}

# input file
# output file
pnsconfig['paths'] = dict(
    pnshome='/tmp/pns',
    inputdir='/tmp/input',
    inputfiles=['infile'],
    outputdir='/tmp/output',
    outputfile='outfile'
)

# the stateless data processing program that reads from inputdir and
# leave the output in the outputdir. The format is the input for subprocess()
h = pnsconfig['paths']['pnshome']
pnsconfig['scripts'] = dict(
    init=[join(h, 'initPTS'), ''],
    config=[join(h, 'configPTS'), ''],
    prog=[join(h, 'hello'), ''],
    clean=[join(h, 'cleanPTS'), '']
)
del h

# seconds
pnsconfig['timeout'] = 10
