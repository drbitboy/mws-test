# mws-test
Mars Weather Service (MWS) Jupyter/bqplot interactions

This is a minimal repo that implements the behavior we are trying to correct:

  https://github.com/drbitboy/mws-test

Post any queries here at https://gitter.im/jupyter-widgets/Lobby, or email briantcarcich@gmail.com.

The main purpose of posting this is for someone who knows better to look at how we modify the brushes programmatically, when the OP brush is moved, or when one of the green 95% buttons are pressed.  Please feel free to clone/fork, add branches, and issue Pull Requests as you see fit e.g. adding comments or better code.

Comments and criticisms are equally welcome.

Thanks!

## Operational details

We find we have to to [Restart] the kernel to get it working initially.

The top plot (Overview Panel; OP) is an overview plot of all data loaded: select the last Sol - Martian day - you want to seeand the number of Sols, and then click the [Load] button

After that, modify the brush in the OP to change (zoom in on) which data you want to see in the next plot down (Data Selector; DS).

After that, modify the brush in the DS to change (zoom in on) which data you want to see in the bottom six plots (Analysis Panel; AP).

The green [<] and [>] buttons shift the DS brush by 95% of its width, thought limited by the DS plot bounds, which in turn are equal to the OP brush limits.

You can turn on and off visual plotting of the individual points, as visual circles on top of the lines in a plot, by clicking its [Mark] checkbox on the right.

You can enable brushing in each the AP plots by clicking its [Brush] checkbox on the right.

If there are more than one AP brushes enabled, modifying one should modify them all, but if the AP plot range is small enough, there will be a humorous display. I don't know why it doesn't turn into an infinite loop.

The file mws_log.txt records all of the callbacks, and a bit more for the 95% button callbacks; doing

    tail -f mws_log.txt

while running the notebook is interesting.

## Known issues

The biggest problem we have is that we have a hard-to-reproduce, intermittent problem:  sometimes, when the OP brush is moved, the DS brush apparently loses its callback (brushDs.observe(on_brushDs)), after which modifying the DS brush with the mouse fails to update the AP plots; however, the green 95% buttons do still move the AP plot range.

A confusing aspect of the brush behavior when changing brushes programmatically is that if we change the brush limit values just once, they are not updated in the displate.  Our workaround has been to set brush.selected to the new values with a slight offset (0.001), and then set them to to the desired new values.  I *think* this has something to do with the .brushing property that normally is set True at the start (mouse-down) of a mouse and then is set False at the end (mouse-up), but that is just a guess at this point.

Another confusing aspect of all of this is many, many "after the fact" callbacks, driven by [hold trait notifications]; I wonder if those are the actual problem, or perhaps if the way we are programmatically updating the brushes is causing the undesired [hold trait notifications] activities.

Another problem is keeping visible AP brushes lined up when one of them is changed.

The callback for the OP brush is on_brushOv in qoverview.py.  It modifies the DS plot limits and replots the data in the DS plot; if the existing DS brush limits are outside the DS plot limits, it also modifies (truncates or shifts) the DS brush, which in turn modifies the AP plot limits.

The callback for the DS brush is on_brushDs in qdataselector.py.

At some point I may add some better comments in the about what is happening.

## Miscellany

The data are synthetic; the algorithm is in db_module.py.

The conversion from SCLK (spacecraft clock) to UTC and to Local Mean Solar Time (LMST) are also in db_module.py.  Those algorithm are trimmed down versions approximating what we get from NAIF/SPICE (cf. http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/, specifically http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/sclk/insight_lmst_2016e09o_v1.tsc and http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/lsk/naif0012.tls ).
