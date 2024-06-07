import base64
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib as mpl
import matplotlib.pyplot as plt

from shapely.geometry.point import Point
import contextily as cx

def display_benchmarking(df):

    df['BUpolygon'] = gpd.GeoSeries.from_wkt(df['BUpolygon'])
    gdf = gpd.GeoDataFrame(df, geometry='BUpolygon', crs=4326)
    gdf["KPIaValueBUmax"] = gdf["KPIaValueBUmax"].astype(float)

    points = gpd.GeoSeries([Point(2.17-0.5, 41.442), Point(2.17+0.5, 41.442)], crs=4326)  # Geographic WGS 84 - degrees
    points = points.to_crs(32619) # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])

    # mpl.style.use('default')

    scale1 = ScaleBar(dx=distance_meters, location='lower right', scale_loc='bottom')

    fig = Figure()
    ax1 = fig.subplots()

    ax = gdf.plot(column="KPIaValueBUmax",cmap="RdYlGn_r",scheme='QUANTILES', k=4,legend=True,
                  edgecolor="k",alpha=0.8,ax=ax1)#legend_kwds={'loc': 'center left', 'bbox_to_anchor': (1, 0.5)})
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, crs=gdf.crs)
    ax.add_artist(scale1)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    figdata = base64.b64encode(buf.getbuffer()).decode("ascii")
    return figdata
