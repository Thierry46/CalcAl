"""
************************************************************************************
Class : DateUtil
Role : Utilities to convert Dates
Date : 25/11/2016
************************************************************************************
"""
import string
import datetime

def formatDate(dateStr):
    """ Check and format a given date
        return YYY/MM/DD or ValueError exception if problem """

    # Check separators
    sepList = []
    for car in dateStr:
        if car not in string.digits:
            sepList.append(car)
    if len(sepList) == 0:
        raise ValueError(_("No separator in the date") + " " + dateStr)
    if len(set(sepList)) > 1:
        raise ValueError(_("Too many different separators in the date") + " " +
                         dateStr + " : " + str(set(sepList)))
    if sepList[0] != '/':
        dateStr = dateStr.replace(sepList[0], '/')

    dateParsed = None
    for formatList in ['%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d']:
        try:
            dateParsed = datetime.datetime.strptime(dateStr, formatList)
            break
        except ValueError:
            pass
    if dateParsed is None:
        raise ValueError(_("Date is not valid") + " " + dateStr)

    dateFormated = '{:04d}/{:02d}/{:02d}'.format(dateParsed.year, dateParsed.month, dateParsed.day)
    return dateFormated
