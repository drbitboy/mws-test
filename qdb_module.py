import os
import numpy
import datetime
import pandas as pd
import qconfig as c

try:
    twopi
except:
    twopi = 2.0 * numpy.pi
    s_per_sol = 88775.244
    sample_per_sol = int(os.environ.get('SPS',3000))
    s_per_sample = s_per_sol / float(sample_per_sol)
    i_arr = numpy.arange(sample_per_sol,dtype=numpy.float)
    radian_arr = twopi * i_arr / sample_per_sol
    s_arr = i_arr * s_per_sample
    sclk_zero_epoch = datetime.datetime(2000,1,1,12,0,0)
    sol_zero_epoch = datetime.datetime(2018,11,26,19,46,28) + datetime.timedelta(seconds=.6820)
    zero_sol_sclk = (sol_zero_epoch - sclk_zero_epoch).total_seconds()
    sclk_to_utc = lambda sclk: (sclk_zero_epoch + datetime.timedelta(seconds=sclk)).isoformat()[:19]


########################################################################
def sclk_to_lmst(sclk):

    sol_s = (sclk-zero_sol_sclk) * 864e2 / s_per_sol
    sol_td = datetime.timedelta(seconds=sol_s)

    return '{:05d}M{:02d}:{:02d}:{:02d}'.format(
      sol_td.days
     ,int(sol_td.seconds/3600)
     ,int((sol_td.seconds%3600)/60)
     ,int(sol_td.seconds%60)
     )


########################################################################
def sclks_convert(sclks_sequence,time_format):

    if time_format==c.kLMST : func = sclk_to_lmst
    elif time_format==c.kUTC: func = sclk_to_utc
    else                    : func = lambda sclk: 'UNK'

    return list(map(func,sclks_sequence))


########################################################################
def select_by_sol(hilo_sol       ### Pair of Sols
                 , db_name       ### Unused
                 , decimation=1  ### Ignored
                 , required_keys=c.kDataColumnKeys
                 ):
    lo_sol, hi_sol = hilo_sol
    assert isinstance(lo_sol,int)
    assert isinstance(hi_sol,int)
    assert lo_sol>0
    assert hi_sol>0
    assert hi_sol>=lo_sol

    if not required_keys: required_keys = c.kDataColumnKeys

    dt_seriess = dict()

    while True:

        first_sclk = zero_sol_sclk + (s_per_sol * lo_sol)

        for kdata in required_keys:
            phase = twopi * float(c.kDataColumnKeys.index(kdata)) / len(c.kDataColumnKeys)
            series = pd.Series(data=numpy.cos(phase+(lo_sol*radian_arr))
                              ,index=first_sclk+s_arr
                              ,name=kdata
                              )
            series.index.name = 'SCLK'
            if kdata in dt_seriess:
                dt_seriess[kdata] = dt_seriess[kdata].append(series,verify_integrity=True)
            else:
                dt_seriess[kdata] = series

        if lo_sol == hi_sol: break

        lo_sol += 1

    dt_times = {c.kSCLK: [min([dt_seriess[k].index[0] for k in dt_seriess])
                       ,max([dt_seriess[k].index[-1] for k in dt_seriess])
                       ,]
               }
    return dt_times,dt_seriess


########################################################################
if "__main__"==__name__:
    print(dict(sclk_zero_epoch=sclk_zero_epoch
              ,sol_zero_epoch=sol_zero_epoch
              ,zero_sol_sclk=zero_sol_sclk
              ))
