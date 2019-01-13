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


### Attributes which mungit should skip:
mungit_skip = set('scale marks margin padding height display width keys comm color layout tooltip options style'.split())


########################################################################
def mungit(arg,depth=0):
    """Recursively turn classes into strings for do_mws_log_actions"""
    if depth > 5: return str(arg)

    if ( isinstance(arg,bq.interacts.BrushIntervalSelector)
      or isinstance(arg,wg.Checkbox)
      or isinstance(arg,wg.Dropdown)
      or isinstance(arg,wg.SelectMultiple)
       ):
        ### Special handling for ipywidget class instances:  => dict
        return {str(type(arg)):mungit(vars(arg),depth+1)}

    if isinstance(arg,dict):
        ### Handling for dicts
        rtn = dict()
        for key in arg:

            ### Skip keys in mungit, or keys that are not _trait_values
            ### and start with an underscore
            if key in mungit_skip: continue
            if key!='_trait_values' and key[:1]=='_': continue

            ### Recurse value associated with key
            rtn[key] = mungit(arg[key],depth+1)
        return rtn

    try:
        ### Handle sequences (lists, tuples)
        rtn = list()
        for item in arg: rtn.appen(mungit(item,depth+1))
        return rtn
    except:
        ### Handle anything not handled above
        return str(arg)


########################################################################
s_htn = 'hold_trait_notifications'
def do_mws_log_actions(arg):
    """
    Log actions if qmws_logactions.py was imported
    Return True if call stack includes method hold_trait_notifications

    """

    ### Return variable:  True IFF hold_trait_notifications was found
    found_htn = False

    try:

        ### If qmws_log_actions wasn't imported, only look at call stack
        if qmws_log_actions is None:
            depth = 1
            while depth:
                try:
                    if s_htn == sys._getframe(depth).f_code.co_name:
                        return True
                    depth += 1
                ### Assume exception indicates end of call stack
                except: return False

        ### Open log file
        with open(mws_log_file,'a') as f_log:

            ### Traverse call stack
            depth = 1
            callers = []
            while depth:
                try:
                    caller = sys._getframe(depth).f_code.co_name
                    callers.append(caller)
                    ### Set found_htn IFF hold_trait_notifications found
                    if not found_htn: found_htn = caller == s_htn

                    depth += 1
                ### Assume exception indicates end of call stack
                except: break

            ### Get UTC and JSON string for argument
            utc = datetime.datetime.now().isoformat()
            arg_json = mungit(arg)

            ### Write to log file
            f_log.write('========================================================================\n{}\n'.format(
                       sj.dumps(dict(callers=callers,utc=utc,data=arg_json))
                       ))
    except:
            import traceback
            traceback.print_exc()

    ### Return whether hold_trait_notifications was in call stack
    return found_htn


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
### Prefix for setTimeValues assignments to dtLabels
dt_prefix_times = dict(
[(ktime
 ,('<p style="margin: 0px 0px 0px 0px; line-height : 1em;">'
   '<span style="color: red; margin: 0px 0px 0px 0px; line-height : 1em;">{}: '
  ).format(ktime)
 ,)
 for ktime in c.kTimeKeys
])


########################################################################
def setTimeValues(dtLabels, minSclk, maxSclk):

    """Set values of the labels that display Time range"""

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
    """Update .value text in error message widget, c.globalErrorMsg"""
    if not (newErrorMsg is None): c.globalErrorMsg = str(newErrorMsg).replace('\n','//')
    try   : c.lbErrorMsg.value = str(c.globalErrorMsg)
    except: pass
