#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
************************************************************************************
program : CalcAl
Author : Thierry Maillard (TMD)
Date : 10/3/2016 - 8/5/2016

Object : Food Calculator based on CIQUAL Tables.
    https://pro.anses.fr/tableciqual

Options :
    -h ou --help : Display this help message.
    -d ou --debug : Verbose mode when starting
    
Paramèters : None.

Licence : GPLv3
Copyright (c) 2016 - Thierry Maillard


This file is part of CalcAl project.

CalcAl project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CalcAl project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CalcAl project.  If not, see <http://www.gnu.org/licenses/>.
************************************************************************************
"""
import sys
import getopt
import gettext
import os
import os.path
import configparser
import platform
import locale
import logging
from logging.handlers import RotatingFileHandler
import imp # To test if a module is available

from gui import CalcAlGUI

##################################################
# main function
##################################################
def main(argv=None):
    """
    Get options, set logging system and launch GUI
    """
    isModeDebug = False
    #############################
    # Analyse des arguments reçus
    #############################
    if argv is None:
        argv = sys.argv

        # parse command line options
    try:
        opts, args = getopt.getopt(argv[1:], "hd", ["help", "debug"])
    except getopt.error as msg:
        print(msg)
        print("to get help : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    progName = sys.argv[0]
    dirProject = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    for option, arg in opts:
        if option in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if option in ("-d", "--debug"):
            isModeDebug = True
            print("Debug mode : verbose.")

    # This sets the locale for all categories to the user’s default setting
    # locale.setlocale(locale.LC_ALL, "") doesn't detect locale on windows
    # locale.getdefaultlocale() seems to detect better...
    # Decimal separator is still . (point)
    # Nowdays, french users don't see any advantage to use , (comma)
    # else it would be possible by using locale fucnction instead float(), str(), format()
    # see : https://docs.python.org/3/library/locale.html#locale.format
    currentLocale = locale.getdefaultlocale()
    if not currentLocale:
        print("Can't determine locale to know what langage is used by your computer")
        print("Please set LANG environnement variable")
        print("Example on Windows : set LANG=fr_FR.cp1252")
        print("Example on Mac, Linux, Unix : export LANG=fr_FR.cp1252")
        sys.exit(1)
    locale.setlocale(locale.LC_ALL, currentLocale)

    # Read configuration properties
    fileConfigApp = os.path.join(dirProject, 'CalcAl.ini')
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp)

    # i18n : Internationalization for GUI windows
    pathname = os.path.dirname(sys.argv[0])
    localeDir = configApp.get('Resources', 'LocaleDir')
    localeDirPath = os.path.join(dirProject, localeDir)
    gettext.install("messages", localeDirPath)

    # Détermination mode de fonctionnement
    if len(args) > 1:
        print(__doc__)
        print("Error : 0 ou 1 parameter allowed !")
        sys.exit(1)

    # Start logging message system
    initLogging(configApp, dirProject, isModeDebug)
    logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
    idProg = configApp.get('Version', 'AppName') + ' - version ' + \
             configApp.get('Version', 'Number') + ' du ' + \
             configApp.get('Version', 'Date')

    logger.info("Satrting " + progName + " : " + idProg)

    # Launch GUI
    CalcAlGUI.CalcAlGUI(configApp, dirProject).mainloop()

    logger.info("End of " + progName + " : " + idProg)
    logging.shutdown() # Terminaison système de logging


def initLogging(configApp, dirProject, isModeDebug):
    """ Start logging message system """
    logDir = os.path.join(dirProject, configApp.get('Log', 'DirLog'))
    if not os.path.isdir(logDir):
        os.mkdir(logDir)
    logFileName = configApp.get('Log', 'BaseLogFileName')
    pathLogFileName = os.path.join(logDir, logFileName)
    logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
    if isModeDebug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    fileHandler = RotatingFileHandler(pathLogFileName, 'a',
                                      configApp.getint('Log', 'MaxBytes'), 1)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    streamHandler = logging.StreamHandler()
    if isModeDebug:
        streamHandler.setLevel(logging.DEBUG)
    else:
        streamHandler.setLevel(logging.WARNING)
    logger.addHandler(streamHandler)

##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)



