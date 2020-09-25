import logging
import config

loggers = {}

def getLogger(analysisID=0,host='server'):
    # log file
    logfile = "{}/{}".format(config.dir.log_dir,"{}.log".format(host))
    # create logger
    if loggers.get(host):
        return loggers.get(host)
    else:
        logger = logging.getLogger(host)
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.FileHandler(logfile, mode='a', encoding='utf-8')
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s: [%(levelname)s]['+str(analysisID)+'] - %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)
        loggers[host] = logger
        return logger