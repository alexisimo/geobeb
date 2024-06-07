import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np

def display_benchmarking(data, bins):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax1 = fig.subplots()
    n, bins, patches = ax1.hist(data, bins=bins, lw=1, ec="white", fc="red", alpha=1, weights = [1/len(data)] * len(data),
                                label="Absolute", rwidth=0.85)
    ax1.set_xlabel('Annual Non-renewable Energy Use Intensity ($kWh/m^2$)')
    ax1.set_ylabel('Percent frequency')

    ax2 = ax1.twinx()
    ax2.margins(0)
    middleBins = bins + (bins[1] - bins[0]) / 2
    ax2.plot(middleBins[0:-1], np.cumsum(n), "b-", marker=".", lw=1, label="Cummulative")
    # ax2.hist(data, bins=bins, density=True, histtype='step', ec="green", cumulative=True, label='Cummulative')
    ax2.axvline(x=np.median(data), c='black', ls="-", label='Median')
    ax2.vlines(np.quantile(data,[0.25,0.75]),0,1,ls="--",color="gray",lw=1, label="Quartiles")
    ax2.annotate('Peer group: \n' + str(len(data)) + " building spaces", (0.67,0.75),xycoords='figure fraction')
    ax2.text(np.median(data)-0.016*np.max(data), 1.025, '$\downarrow$Benchmark: ' + str(round(np.median(data),2)) + "($kWh/m^2$)")
    ax2.set_ylabel('Cummulative percent frequency')

    ax2.legend(loc="center right")

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    figdata = base64.b64encode(buf.getbuffer()).decode("ascii")
    return figdata
