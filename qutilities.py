import os
import sys
import datetime
import bqplot as bq
import ipywidgets as wg
try: import simplejson as sj
except: import json as sj
from bisect import bisect_left

import qconfig as c
from qdb_module import sclks_convert
try:
    import qmws_log_actions
    try: mws_log_file = qmws_log_actions.mws_log_file
    except: mws_log_file = 'mws_log.txt'
except:
    qmws_log_actions = None

mungit_skip = set('scale marks margin padding height display width keys comm color layout tooltip options style'.split())
def mungit(arg,depth=0):
    if depth > 5: return str(arg)
    from qdataselector import EMPTY
    if ( isinstance(arg,bq.interacts.BrushIntervalSelector)
      or isinstance(arg,wg.Checkbox)
      or isinstance(arg,wg.Dropdown)
      or isinstance(arg,wg.SelectMultiple)
       ):
        return {str(type(arg)):mungit(vars(arg),depth+1)}
    if isinstance(arg,dict):
        rtn = dict()
        for key in arg:
            if key in mungit_skip: continue
            if key!='_trait_values' and key[:1]=='_': continue
            rtn[key] = mungit(arg[key],depth+1)
        return rtn
    try:
        rtn = list()
        for item in arg: rtn.appen(mungit(item,depth+1))
        return rtn
    except:
        return str(arg)


########################################################################
def do_mws_log_actions(arg):
    try:
        if qmws_log_actions is None: return
        with open(mws_log_file,'a') as f_log:

            depth = 1
            callers = []
            while depth:
                try:
                    callers.append(sys._getframe(depth).f_code.co_name)
                    depth += 1
                except: break

            utc = datetime.datetime.now().isoformat()
            arg_json = mungit(arg)
            f_log.write('========================================================================\n{}\n'.format(
                       sj.dumps(dict(callers=callers,utc=utc,data=arg_json))
                       ))
    except:
            import traceback
            traceback.print_exc()


########################################################################
def takeClosestIndex(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest index to myNumber.
    If two numbers are equally close, return the index of the smallest number.
    """
    # With thanks to Lauritz V. Thaulow for the following code
    # Return the value from the list that is closest to myNumber
    pos = bisect_left(myList, myNumber)
    if pos == 0: return pos
    if pos == len(myList): return pos - 1
    before = myNumber - myList[pos - 1]
    after = myList[pos] - myNumber
    return pos - ((after > before) and 1 or 0)


########################################################################
dt_prefix_times = None
def setTimeValues(dtLabels, minSclk, maxSclk):

    """Set values of the labels that display Time range"""

    global dt_prefix_times

    if dt_prefix_times is None:
        dt_prefix_times = dict([(ktime
        , ('<p style="margin: 0px 0px 0px 0px; line-height : 1em;">'
           '<span style="color: red; margin: 0px 0px 0px 0px; line-height : 1em;">{}: '
          ).format(ktime)
        , ) for ktime in c.kTimeKeys])

    dtTimeFormat={c.kSCLK: "</span>{}<br /><span style='padding-left:41px;'>&Delta; = {}</span></p>"
                 ,c.kLMST:  "</span>{}<br /><span style='padding-left:34px;'>{}</span></p>"
                 ,c.kUTC:  "</span>{}<br /><span style='padding-left:34px;'>{}</span></p>"
                 }

    for ktime in c.kTimeKeys:
        if ktime==c.kSCLK:
            # SCLK is a special case in that we want to show the start time
            # followed by the duration in seconds.
            value = dt_prefix_times[ktime] + dtTimeFormat[ktime].format('%.1f'%(minSclk,), '%.1f'%(maxSclk-minSclk,))
        else:
            value = dt_prefix_times[ktime] + dtTimeFormat[ktime].format(*sclks_convert((minSclk,maxSclk,),ktime))

        dtLabels[ktime].value = value


########################################################################
def updateErrorMsg(newErrorMsg=None):
    if not (newErrorMsg is None): c.globalErrorMsg = str(newErrorMsg).replace('\n','//')
    try   : c.lbErrorMsg.value = str(c.globalErrorMsg)
    except: pass
