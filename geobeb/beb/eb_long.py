import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np

def display_benchmarking(df):
    data = []
    medians = []
    for year in range(2013, 2023):
        data.append(df[df["KPIaYear"] == year]["KPIaValue"])
        medians.append(np.median(data[-1]))

    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax1 = fig.subplots()
    # ax1 = fig.add_subplot(111)
    ax1.margins(0)
    ax1.set_ylabel('Annual Non-renewable Energy Use Intensity ($kWh/m^2$)')
    ax1.set_xlabel('Year')

    ax1.axis([0, 11, 0, 750])
    # ax1.axis("off")
    # ax1.bar(range(1,11),medians, color="")
    ax1.text(0, 800, 'Peer group:  (building spaces)')
    for i in range(0, 10):
        ax1.text(i+0.7, 760, str(len(data[i])))

    ax1.boxplot(data, vert=True, sym=".", labels=range(2013, 2023), notch=True, showbox=False, showcaps=True)
    ax1.violinplot(data, vert=True, showmedians=True)
    ax1.plot(range(1, 11), medians, color="black")

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    figdata = base64.b64encode(buf.getbuffer()).decode("ascii")
    return figdata
