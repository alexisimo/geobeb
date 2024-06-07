import base64
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import geopandas as gpd
import geoplot as gplt

from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib as mpl
import matplotlib.pyplot as plt

from shapely.geometry.point import Point
import contextily as cx

def display_benchmarking(df,wkt="POLYGON((2.1701109084663988 41.385534418977755,2.171666589695037 41.38301886727217,2.174026933628142 41.38030196212546,2.175467279888924 41.37867176460654,2.17768010230103 41.37571315357127,2.177894679022221 41.37596474138101,2.178203133058934 41.37597480487318,2.182253268647041 41.38126798591341,2.1727582488248496 41.388452337008545,2.1701109084663988 41.385534418977755))"):

    df['BUpolygon'] = gpd.GeoSeries.from_wkt(df['BUpolygon'])
    df["ADpoint"] = gpd.GeoSeries.from_wkt(df['ADpoint'])
    gdf = gpd.GeoDataFrame(df, geometry='BUpolygon', crs=4326)
    gdf["KPIaValueBUmax"] = gdf["KPIaValueBUmax"].astype(float)
    gdfAD = gpd.GeoDataFrame(df, geometry='ADpoint', crs=4326)

    points = gpd.GeoSeries([Point(2.17-0.5, 41.442), Point(2.17+0.5, 41.442)], crs=4326)  # Geographic WGS 84 - degrees
    points = points.to_crs(32619) # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])

    # mpl.style.use('default')

    scale1 = ScaleBar(dx=distance_meters, location='lower right', scale_loc='bottom')

    fig = Figure()
    ax1 = fig.subplots()

    ax = gplt.kdeplot(gdfAD[["KPIaValueBUmax", "ADpoint"]], ax=ax1, cmap='YlOrRd', fill=True, thresh=0.2, alpha=0.4,)
                      # clip=gpd.GeoSeries.from_wkt([wkt]))
    gdf.plot(column="KPIaValueBUmax", cmap="RdYlGn_r", scheme='QUANTILES', k=4, legend=True,
             edgecolor="k", alpha=0.8, ax=ax)
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, crs=gdf.crs)
    ax.add_artist(scale1)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    figdata = base64.b64encode(buf.getbuffer()).decode("ascii")
    return figdata
