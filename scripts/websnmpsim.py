# -----------------------------------------------------------
#
# Web GUI for snmpsim (http://snmpsim.sourceforge.net)
#
# This is a small Twisted program that provides a Web interface on the
# .snmprec files used by the snmpsimd.py SNMP Simulator program to
# respond with simulated SNMP data. It does several things:
#
# 1) It launches snmpsimd.py, so that the simulator itself runs normally.
# 2) It provides a small web server GUI on port 8880 to list all the
#    simulated device files and the associated SNMP community strings.
# 3) It allows you to add .snmprec files to the current directory. When
#    you add a file, it stops and restarts snmpsimd.py using the new file
#
# To use the websnmpsim.py program:
# 
# - Retrieve the repository from github. It's at:
# 	https://github.com/richb-hanover/websnmpsim
# - Install the project (sudo python setup.py install)
# - Then cd to the snmpsim/scripts directory 
# - Run it from a terminal window by typing: python scripts/websnmpsim.py
#   snmpsimd.py will be running on the address/port indicated in the
#   web GUI.
# - Connect to the web GUI at: http://localhost:8880
# - To upload a .snmprec file to the current directory, click Browse to
#   select a file, then click Add
# - Ctl-C in the terminal window to abort the program
#
# Prequisites: You may need to install the following packages/modules  
#	before snmpsimd.py and websnmpsim.py will run:
#		easy_install (install this first to get the others)
#		twisted
#		pyasn1
#		pysnmp 
#
# WARNING: Although this program seems to work, it is a two-weekend hack.
#    I wanted to learn a little about Twisted, so this program was
#    a decent vehicle for that learning. I make no claim to the value
#    of this as a starting point for further work.
#
#    Since snmpsimd.py is already based on Python's asyncore, that module
#    may be a better base for long-term development. In fact, the are
#    a lot of lines of communication between the Web GUI and snmpsimd.py
#    which argues that they should be combined.
#
# Please let me know if this is useful for you, or contribute your
# changes back to the snmpsim project. http://snmpsim.sourceforge.net
#
# Rich Brown, Hanover NH USA, richb.hanover@gmail.com
#
# -----------------------------------------------------------

import os
import cgi
import urllib
import time
import socket
import subprocess
import sys
import re
import pprint

from twisted.web.server import Site
import twisted.web.resource
from twisted.internet import reactor, protocol
from twisted.web.static import File, DirectoryLister, getTypeAndEncoding, formatFileSize


class MyDirectoryLister(DirectoryLister):

    # Overrides the standard DirectoryLister to provide a different page template
    # and information for each line of the directory.

    errorStr = ""                   # strings to be set elsewhere and get plugged into the template
    includeStr = ""

    linePattern = '''\
        <tr class="%(class)s">
        <td><a href="%(href)s">%(text)s</a></td>
        <td>%(size)s</td>
        <td>%(type)s</td>
        <td>%(mtime)s</td>
        <td class="code">%(commstr)s</td>
        </tr>
        '''

    template = '''\
<html>
<head>
    <title>Web GUI for snmpsimd</title>
    <style>
        .even-dir { background-color: #efe0ef }
        .even { background-color: #eee }
        .odd-dir {background-color: #f0d0ef }
        .odd { background-color: #dedede }
        .icon { text-align: center }
        .listing {
            margin-left: auto;
            margin-right: auto;
            width: 50%%;
            padding: 0.1em;
        }
        .code { font-family: monospace; }

        body { border: 0; padding: 10px; margin: 0; background-color: #efefef; }
        h1 { padding: 0.1em; background-color: #777; color: white; }
        th { text-align: left; }
        .error { color: red; }
    </style>
</head>

<body>
<h1>Web GUI for snmpsimd</h1>

<p>The files and folders below contain the results of SNMP walks.
Each is addressed by a different community string listed in the rightmost column.
For more information, visit the
<a href=\"http://snmpsim.sourceforge.net\" target=\"_blank\">snmpsim project</a>
on sourceforge.net or <a href=\"https://github.com/richb-hanover/websnmpsim\" target=\"_blank\">
get the source</a> from github.com.</p>
<p>The snmpsim simulator is currently listening on the address %(ip)s, port %(port)s.
Send SNMP queries to this address &amp; port using one of
the community strings listed below to see the responses.
To try it out, copy/paste this line into a terminal:</p>
<blockquote class='code'>snmpwalk -v2c -c public %(ip)s:%(port)s 1.3.6</blockquote>

<p>
<table>
    <thead>
    <tr>
        <th>Filename</th>
        <th>Size</th>
        <th>Content type</th>
        <th>Mod. date</th>
        <th>Community string</th>
    </tr>
    </thead>
    <tbody>
    %(tableContent)s
    </tbody>
</table>
</p>
<p>
    <h3>Adding SNMP Data to the simulator:</h3>
    Select a file and click <b>Add</b> a file to the SNMP Simulator.
    It can handle .snmprec, .snmpwalk or .sapwalk files.<br />
    <form method="post" action="/" enctype="multipart/form-data">
    <input type="file" name="the-file">
    <input type="hidden" name="the-path" value="%(path)s">
    <input type="submit" name="submit" value="Add">
    </form>
    <i>Note:</i> Adding a file makes its SNMP data completely public.
    We think this is a good thing. But you should make sure there is no proprietary information present
    before posting it.
    Although SNMPWalk information generally does <i>not</i> contain community strings,
    you should still check the data first.
</p>
<p class="error">%(errorStr)s</p>
%(includeStr)s
</body>
</html>
	'''

##   _getFilesAndDirectories is just a copy of the original function found in the File class,
    ##   with minor modifications to display useful info about snmpsim .snmprec files

    def _getFilesAndDirectories(self, directory):
        """
        Helper returning files and directories in given directory listing, with
        attributes to be used to build a table content with
        C{self.linePattern}.

        @return: tuple of (directories, files)
        @rtype: C{tuple} of C{list}
        """

        files = []
        dirs = []
        dirs.append({'text':"<i>Parent Directory</i>", 'href': "..",
                    'size': '', 'type': '',
#                    'encoding': '',
                    'mtime': "",
                    'commstr': ""
        })
        for path in directory:
            if path[0] == ".":      # ignore filenames that begin with "."
                continue
            mtime = time.asctime(time.localtime(os.path.getmtime(os.path.join(self.path, path))))

            url = urllib.quote(path, "/")
            escapedPath = cgi.escape(path)
            # print "path %s url %s escapedPath %s" %(path, url, escapedPath)
            if os.path.isdir(os.path.join(self.path, path)):
                url = url + '/'
                dirs.append({'text': escapedPath + "/", 'href': url,
                             'size': '', 'type': '[Directory]',
#                             'encoding': '',
                             'mtime': mtime,
                             'commstr': ''
                })
            else:
                mimetype, encoding = getTypeAndEncoding(path, self.contentTypes,
                    self.contentEncodings,
                    self.defaultType)
                try:
                    size = os.stat(os.path.join(self.path, path)).st_size
                except OSError:
                    continue

                extension = os.path.splitext(path)[1]
                if extension == ".dbm":					# ignore .dbm files
                    continue
                if extension == ".db":                  # if it's ".db"
                    str = path[:-3]
                    extension = os.path.splitext(str)[1]
                    if extension == ".dbm":             # and if there's also a ".dbm"
                        continue                        # just ignore it - MacOSX (esp. Mountain Lion) likes to
                                                        # add .dbm.db (see comment in snmpsimd.py) - so don't show it


                theCommStr = ""
                if (extension == ".snmprec") or (extension == ".sapwalk") or (extension == ".snmpwalk"):
                    bdLen = len(myBaseDir) + len("/data/")
                    theCommStr = self.path[bdLen:]      # get the path up to .../data
                    if theCommStr != "":                # if it's non-empty
                        theCommStr += "/"               # append the "/"
                    theCommStr += path[:-len(extension)]   # append the file name, less the extension

                ## ** Comment **
                ##   Add attributes the the "elements" displayed in each line

                files.append({
                    'text': escapedPath, "href": url,
                    'type': '[%s]' % mimetype,
#                    'encoding': (encoding and '[%s]' % encoding or ''),
                    'size': formatFileSize(size),
                    'mtime': mtime,
                    'commstr': theCommStr,
                    }
                )
        return dirs, files

    def render(self, request):
        """
        Render a listing of the content of C{self.path}.
        """
        request.setHeader("content-type", "text/html; charset=utf-8")
        if self.dirs is None:
            directory = os.listdir(self.path)
            directory.sort()
        else:
            directory = self.dirs
        # print ("----- path %s" % self.path)
        dirs, files = self._getFilesAndDirectories(directory)

        tableContent = "".join(self._buildTableContent(dirs + files))

        retval =  self.template % \
               {"tableContent": tableContent,
                "ip":           myIPadrs,
                "port":         snmpsimPort,
                "path":         self.path[len(myBaseDir)+len("/data/"):],
                "includeStr":   MyDirectoryLister.includeStr,
                "errorStr":     MyDirectoryLister.errorStr }
        MyDirectoryLister.errorStr = ""                       # clear for the next time
        return retval

class FormPage(File):

    # if URL is root (".../"), redirect to "/snmp/" URL
    def render_GET(self, request):
        request.redirect('/snmp/') # http://stackoverflow.com/questions/8128045/twisted-web-redirects-in-request
        return ''

    # handle a post to the root, which should contain a file to add to the specified directory
    def render_POST(self, request):
        MyDirectoryLister.errorStr = ""                 # no errors yet
        snmpsimProcess.stopProc()                       # stop snmpsimd.py
        # pprint.pprint(request.__dict__)               # show what data we've received

        path = request.args.get('the-path')[0]          # web form has path to this directory
        fileData = request.args.get('the-file')[0]      # get the contents of the uploaded file as well
        # code from http://stackoverflow.com/questions/3275081/am-i-parsing-this-http-post-request-properly
        self.headers = request.getAllHeaders()
        img = cgi.FieldStorage(                         # For the parsing part look at [PyMOTW by Doug Hellmann][1]
            fp = request.content,
            headers = self.headers,
            environ = {'REQUEST_METHOD':'POST',
                       'CONTENT_TYPE': self.headers['content-type'],
                       }
        )
        fileName = img["the-file"].filename             # and finally the name of the uploaded file

        if fileName != "":                              # save it if it's not empty
            fullPath = os.path.join(myBaseDir, "data", path, fileName)
            # print "Data: %s" % (fileData)
            # print "path %s fullpath %s file %s" % (path, fullPath, fileName)
            print "Saving devices%s%s%s%s" % (os.sep, path, os.sep, fileName)
            saveFile(fullPath, fileData)
        else:                                           # otherwise, complain...
            MyDirectoryLister.errorStr = 'Please select a file before clicking <b>Add</b>...'

        snmpsimProcess.startProc()                      # restart the snmpdimd.py program
        request.redirect('/snmp/%s' % (path))
        return ''


class MyFile(File):

    def directoryListing(self):
        return MyDirectoryLister(self.path,
            self.listNames(),
            self.contentTypes,
            self.contentEncodings,
            self.defaultType)

class SNMPSimProcess():
    def __init__(self,args):
        self.argstr = args
        self.myProcess = None
    def startProc(self):
        snmpsimexecpath = os.path.join(myScriptDir, "snmpsimd.py")
        self.myProcess = subprocess.Popen([sys.executable, snmpsimexecpath, self.argstr])
        print "Started snmpsimd.py child"
    def stopProc(self):
        print "Stopping snmpsimd.py child"
        self.myProcess.terminate()
        self.myProcess = None

def saveFile(path, aStr):
    """
    Given a file path (string) and some text, save that text to the named path.
    """
    f = open(path, 'w')
    f.write(aStr)
    f.close()


# =======
# astr = '''\
# 1.3.6.1.2.1.1.1.0|4|a*.snmprec
# 1.3.6.1.2.1.1.2.0|6|1.3.6.1.4.1.30803
# '''

# Install a mimetype for the .snmprec files
File.contentTypes.update({ '.snmprec': 'text/plain', })
File.contentTypes.update({ '.sapwalk': 'text/plain', })
File.contentTypes.update({ '.snmpwalk': 'text/plain', })

# directory of the current executable
# http://stackoverflow.com/questions/4934806/python-how-to-find-scripts-directory
myScriptDir = sys.path[0]
# print "BaseDir1: " + myScriptDir
myBaseDir = os.path.dirname(myScriptDir)    # directory of overall snmpsim project
# print "BaseDir2: " + myBaseDir

# Network id's - get a usable IP address for this computer
# http://www.linux-support.com/cms/get-local-ip-address-with-python/
myPort = 8880
snmpsimPort = 1161
myIPadrs = ""
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('www.google.com', 8000))
    myIPadrs = s.getsockname()[0]
    s.close()
except:
    pass

# set up machinery to start/stop the snmpsimd.py process
simArgs = '--agent-udpv4-endpoint=%s:%d' % ('0.0.0.0', snmpsimPort) # listen on any IPv4 interface
snmpsimProcess = SNMPSimProcess(simArgs)
snmpsimProcess.startProc()

MyDirectoryLister.errorStr = ""                         # no errors to start
MyDirectoryLister.includeStr = ""                       # no includes to start
myIncludes = os.path.join(myScriptDir,"webincludes.html")
if os.path.exists(myIncludes):                  # but check the 'webincludes.html' file
    f = open(myIncludes, "r")
    MyDirectoryLister.includeStr = f.read()
    f.close()

# and set up twisted machinery itself
root = twisted.web.resource.Resource()
dataFolder = os.path.join(myBaseDir, "data")
theFile = MyFile(dataFolder)
root.putChild("snmp", theFile)  # files served out from / come from the "data" directory
root.putChild("",FormPage(dataFolder))

factory = Site(root)
reactor.listenTCP(myPort, factory)
print "Starting Web GUI for snmpsim on port %d" % (myPort)
reactor.run()                   # when the main process stops, it takes down the snmpsimd process as well
print "Stopping Web GUI for snmpsim"

