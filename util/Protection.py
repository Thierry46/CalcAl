"""
************************************************************************************
Class : Protection
Role : Utilities functions used to protect software for unallowed usage
Date : 25/6/2017
************************************************************************************
"""
import hashlib

def generateCryptingKey(logger, plateformId, userId, userDir):
    """ Generate a crypting key according parameters
        return a sha224 key (56 letters and digits long """

    identification = plateformId + ' : ' + userId + ' : ' + userDir
    logger.info(_("Created a cryptographic key for") +  identification)

    key = hashlib.sha224(identification.encode('utf-8')).hexdigest()
    logger.info(_("Key : ") + key)

    return key
