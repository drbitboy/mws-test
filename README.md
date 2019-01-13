# mws-test
Mars Weather Service (MWS) Jupyter/bqplot interactions

This is a minimal repo that implements the behavior we are trying to correct:

  https://github.com/drbitboy/mws-test

Post any queries here at https://gitter.im/jupyter-widgets/Lobby, or email briantcarcich@gmail.com.

Thanks!

## Details

The top plot (Overview Panel; OP) is an overview plot of all data loaded: select the last Sol - Martian day - you want to seeand the number of Sols, and then click the [Load] button

After that, modify the brush in the OP to change (zoom in on) which data you want to see in the next plot down (Data Selector; DS).

After that, modify the brush in the DS to change (zoom in on) which data you want to see in the bottom six plots (Analysis Panel; AP).

The green [<] and [>] buttons shift the DS brush by 95% of its width, thought limited by the DS plot bounds, which in turn are equal to the OP brush limits.

You can turn on and off visual plotting of the individual points, as visual circles on top of the lines in a plot, by clicking its [Mark] checkbox on the right.

You can enable brushing in each the AP plots by clicking its [Brush] checkbox on the right.

If there are more than one AP brushes enabled, modifying one should modify them all, but if the AP plot range is small enough, there will be a humorous display. I don't know why it doesn't turn into an infinite loop.

Anyway, the main purpose of posting this is for someone who knows better to look at how we modify the brushes programmatically, when the OP brush is moved, or when one of the green 95% buttons are pressed.

It's synthetic data; the algorithm is in db_module.py.

The conversion from SCLK (spacecraft clock) to UTC and to Local Mean Solar Time (LMST) are also in db_module.py.  Those algorithm are trimmed down versions approximating what we get from NAIF/SPICE (cf. http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/, specifically http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/sclk/insight_lmst_2016e09o_v1.tsc and http://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/lsk/naif0012.tls ).
