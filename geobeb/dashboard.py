from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import functools
from geobeb.db import get_db
from geobeb.beb import eb_hist
from geobeb.beb import eb_long
from geobeb.beb import eb_map
from geobeb.beb import eb_heatmap

import pandas as pd
import time

bp = Blueprint('dashboard', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    # Start the chrono
    tic = time.time()
    db = get_db()
    year = 2022
    query = """
        PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
        PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX s4city: <https://saref.etsi.org/saref4city/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        SELECT DISTINCT ?BScadastralReference ?KPIaValue WHERE{
          ?CP a bigg:CadastralParcel;
              geosp:sfContains ?BU.
          ?BU a s4agri:Building;
              rdfs:label ?BUcadastralReference;
              geosp:sfContains ?BS.
          ?BS a s4agri:BuildingSpace;
              rdfs:label ?BScadastralReference;
              bigg:mainUse/skos:prefLabel "Residential".
          ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                s4city:assesses ?BS;
                saref:hasValue ?KPIaValue;
                s4city:hasCreationDate ?KPIaDate.
          FILTER (YEAR(?KPIaDate) = 2022 )
          {
            SELECT DISTINCT ?CP WHERE{
                        ?CP a bigg:CadastralParcel;
                            vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                        FILTER (geof:sfWithin(?ADpoint, "POLYGON((2.1701109084663988 41.385534418977755,2.171666589695037 41.38301886727217,2.174026933628142 41.38030196212546,2.175467279888924 41.37867176460654,2.17768010230103 41.37571315357127,2.177894679022221 41.37596474138101,2.178203133058934 41.37597480487318,2.182253268647041 41.38126798591341,2.1727582488248496 41.388452337008545,2.1701109084663988 41.385534418977755))"^^geosp:wktLiteral ))
                    } 
          }
        } 
        """
    db.setQuery(query)
    # Run query and store its results
    results = db.query().bindings
    df = pd.DataFrame()
    i = 1
    for result in results:
        row = pd.DataFrame({"index": i,
                            "BScadastralReference": [result["BScadastralReference"].value],
                            "KPIaValue": [result["KPIaValue"].value]
                            }, index=[i])
        df = pd.concat([df, row])
        i += 1
    df["KPIaValue"] = df["KPIaValue"].astype("float")
    # Stop the chrono
    toc = time.time()
    # Generate the figure to be displayed
    fig = eb_hist.display_benchmarking(df["KPIaValue"],30)

    if request.method == 'POST':
        wkt = request.form['wktStringTextArea']
        year = request.form['year']

        error = None

        if not wkt:
            year = 2014
            error = "Polygon not valid."

        if error is not None:
            flash(error)
        else:
            # Restart the chrono
            tic = time.time()
            db = get_db()
            query = """
                PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
                PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
                PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX s4city: <https://saref.etsi.org/saref4city/>
                PREFIX saref: <https://saref.etsi.org/core/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
                SELECT DISTINCT ?BScadastralReference ?KPIaValue WHERE{
                  ?CP a bigg:CadastralParcel;
                      geosp:sfContains ?BU.
                  ?BU a s4agri:Building;
                      rdfs:label ?BUcadastralReference;
                      geosp:sfContains ?BS.
                  ?BS a s4agri:BuildingSpace;
                      rdfs:label ?BScadastralReference;
                      bigg:mainUse/skos:prefLabel "Residential".
                  ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                        s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                        s4city:assesses ?BS;
                        saref:hasValue ?KPIaValue;
                        s4city:hasCreationDate ?KPIaDate.
                  {
                    SELECT DISTINCT ?CP WHERE{
                                ?CP a bigg:CadastralParcel;
                                    vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                                FILTER (geof:sfWithin(?ADpoint, "%s"^^geosp:wktLiteral))
                            } 
                  }                        
                  FILTER (YEAR(?KPIaDate) = %s )
                } 
                """ % (wkt, year)
            db.setQuery(query)
            # Run query and store its results
            results = db.query().bindings
            df = pd.DataFrame()
            i = 1
            for result in results:
                row = pd.DataFrame({"index": i,
                                    "BScadastralReference": [result["BScadastralReference"].value],
                                    "KPIaValue": [result["KPIaValue"].value]
                                    }, index=[i])
                df = pd.concat([df, row])
                i += 1
            df["KPIaValue"] = df["KPIaValue"].astype("float")
            # posts = wkt

            # Stop the chrono
            toc = time.time()

            fig = eb_hist.display_benchmarking(df["KPIaValue"],30)
            # return f"<img src='data:image/png;base64,{data}'/>"
            # return render_template('dashboard/index.html', posts=posts)

    # Calculate the elapsed time
    took = round(toc - tic,3)

    return render_template('dashboard/index.html', took=took, fig=fig, year=year)

@bp.route('/longitudinal', methods=('GET', 'POST'))
def longitudinal():
    # Start the chrono
    tic = time.time()
    db = get_db()

    query = """
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ofn: <http://www.ontotext.com/sparql/functions/>
            PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
            PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
            PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
            PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
            PREFIX s4city: <https://saref.etsi.org/saref4city/>
            PREFIX saref: <https://saref.etsi.org/core/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

            SELECT DISTINCT ?KPIaValue (YEAR(?KPIaDate) as ?KPIaYear) WHERE{
                ?CP a bigg:CadastralParcel;
                geosp:sfContains ?BU;
                vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                ?BU a s4agri:Building;
                rdfs:label ?BUcadastralReference;
                geosp:sfContains ?BS.
                ?BS a s4agri:BuildingSpace;
                rdfs:label ?BScadastralReference;
                bigg:mainUse/skos:prefLabel "Residential".
                ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                s4city:assesses ?BS;
                saref:hasValue ?KPIaValue;
                s4city:hasCreationDate ?KPIaDate.
                {
                    SELECT DISTINCT ?CP WHERE{
                                ?CP a bigg:CadastralParcel;
                                    vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                                FILTER (geof:sfWithin(?ADpoint, "POLYGON((2.1701109084663988 41.385534418977755,2.171666589695037 41.38301886727217,2.174026933628142 41.38030196212546,2.175467279888924 41.37867176460654,2.17768010230103 41.37571315357127,2.177894679022221 41.37596474138101,2.178203133058934 41.37597480487318,2.182253268647041 41.38126798591341,2.1727582488248496 41.388452337008545,2.1701109084663988 41.385534418977755))"^^geosp:wktLiteral ))
                            } 
                }
                # FILTER (geof:sfWithin(?ADpoint, "POLYGON((2.1701109084663988 41.385534418977755,2.171666589695037 41.38301886727217,2.174026933628142 41.38030196212546,2.175467279888924 41.37867176460654,2.17768010230103 41.37571315357127,2.177894679022221 41.37596474138101,2.178203133058934 41.37597480487318,2.182253268647041 41.38126798591341,2.1727582488248496 41.388452337008545,2.1701109084663988 41.385534418977755))"^^geosp:wktLiteral))
            }
            """
    db.setQuery(query)
    # Run query and store its results
    results = db.query().bindings

    df = pd.DataFrame()
    i = 1
    for result in results:
        row = pd.DataFrame({"index": i,
                            "KPIaValue": [result["KPIaValue"].value],
                            "KPIaYear": [result["KPIaYear"].value]
                            }, index=[i])
        df = pd.concat([df, row])
        i += 1
    df["KPIaValue"] = df["KPIaValue"].astype("float")
    df["KPIaYear"] = df["KPIaYear"].astype("int")

    # Generate the figure to be displayed
    fig = eb_long.display_benchmarking(df)

    if request.method == 'POST':
        wkt = request.form['wktStringTextArea']

        error = None
        if not wkt:
            error = "Polygon not valid."

        if error is not None:
            flash(error)
        else:
            # Restart the chrono
            tic = time.time()
            db = get_db()
            query = """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ofn: <http://www.ontotext.com/sparql/functions/>
                PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
                PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
                PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
                PREFIX s4city: <https://saref.etsi.org/saref4city/>
                PREFIX saref: <https://saref.etsi.org/core/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

                SELECT DISTINCT ?KPIaValue (YEAR(?KPIaDate) as ?KPIaYear) WHERE{
                    ?CP a bigg:CadastralParcel;
                    geosp:sfContains ?BU;
                    vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                    ?BU a s4agri:Building;
                    rdfs:label ?BUcadastralReference;
                    geosp:sfContains ?BS.
                    ?BS a s4agri:BuildingSpace;
                    rdfs:label ?BScadastralReference;
                    bigg:mainUse/skos:prefLabel "Residential".
                    ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                    s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                    s4city:assesses ?BS;
                    saref:hasValue ?KPIaValue;
                    s4city:hasCreationDate ?KPIaDate.
                    {
                        SELECT DISTINCT ?CP WHERE{
                                    ?CP a bigg:CadastralParcel;
                                        vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                                    FILTER (geof:sfWithin(?ADpoint, "%s"^^geosp:wktLiteral ))
                                } 
                    }
                } 
                """ % (wkt)

            db.setQuery(query)
            # Run query and store its results
            results = db.query().bindings

            df = pd.DataFrame()
            i = 1
            for result in results:
                row = pd.DataFrame({"index": i,
                                    "KPIaValue": [result["KPIaValue"].value],
                                    "KPIaYear": [result["KPIaYear"].value]
                                    }, index=[i])
                df = pd.concat([df, row])
                i += 1
            df["KPIaValue"] = df["KPIaValue"].astype("float")
            df["KPIaYear"] = df["KPIaYear"].astype("int")

            # Generate the figure to be displayed
            fig = eb_long.display_benchmarking(df)

    # Stop the chrono
    toc = time.time()
    # Calculate the elapsed time
    took = round(toc - tic, 3)

    return render_template('dashboard/longitudinal.html', took=took, fig=fig, year="2013-2022")


@bp.route('/heatmap', methods=('GET', 'POST'))
def heatmap():
    # Start the chrono
    tic = time.time()
    db = get_db()
    year = 2014
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX ofn: <http://www.ontotext.com/sparql/functions/>
        PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
        PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
        PREFIX s4city: <https://saref.etsi.org/saref4city/>
        PREFIX saref: <https://saref.etsi.org/core/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

        SELECT DISTINCT ?BUcadastralReference ?BUpolygon ?ADpoint (MAX(?KPIaValue) AS ?KPIaValueBUmax)
        WHERE{
          ?CP a bigg:CadastralParcel;
              geosp:sfContains ?BU;
              vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
          ?BU a s4agri:Building;
              rdfs:label ?BUcadastralReference;
              geosp:hasGeometry/geosp:asWKT ?BUpolygon;
              geosp:sfContains ?BS.
          ?BS a s4agri:BuildingSpace;
              rdfs:label ?BScadastralReference;
              bigg:mainUse/skos:prefLabel "Residential".
          ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                s4city:assesses ?BS;
                saref:hasValue ?KPIaValue;
                s4city:hasCreationDate ?KPIaDate.
           FILTER (YEAR(?KPIaDate) = 2014 )
          {
            SELECT DISTINCT ?CP WHERE{
                        ?CP a bigg:CadastralParcel;
                            vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                        FILTER (geof:sfWithin(?ADpoint, "POLYGON((2.1701109084663988 41.385534418977755,2.171666589695037 41.38301886727217,2.174026933628142 41.38030196212546,2.175467279888924 41.37867176460654,2.17768010230103 41.37571315357127,2.177894679022221 41.37596474138101,2.178203133058934 41.37597480487318,2.182253268647041 41.38126798591341,2.1727582488248496 41.388452337008545,2.1701109084663988 41.385534418977755))"^^geosp:wktLiteral ))
                    } 
          }
        } GROUP BY ?BUcadastralReference ?BUpolygon ?ADpoint
        """
    db.setQuery(query)
    # Run query and store its results
    results = db.query().bindings

    df = pd.DataFrame()
    i = 1
    for result in results:
        row = pd.DataFrame({"index": i,
                            "BUcadastralReference": [result["BUcadastralReference"].value],
                            "BUpolygon": [result["BUpolygon"].value],
                            "KPIaValueBUmax": [result["KPIaValueBUmax"].value],
                            "ADpoint": [result["ADpoint"].value]
                            }, index=[i])
        df = pd.concat([df, row])
        i += 1

    # Stop the chrono
    toc = time.time()
    # Generate the figure to be displayed
    fig = eb_heatmap.display_benchmarking(df)

    if request.method == 'POST':
        wkt = request.form['wktStringTextArea']
        year = request.form['year']

        error = None

        if not wkt:
            year = 2014
            error = "Polygon not valid."

        if error is not None:
            flash(error)
        else:
            # Restart the chrono
            tic = time.time()
            db = get_db()
            query = """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                PREFIX ofn: <http://www.ontotext.com/sparql/functions/>
                PREFIX bigg: <http://bigg-project.eu/ld/ontology#>
                PREFIX geosp: <http://www.opengis.net/ont/geosparql#>
                PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                PREFIX s4agri: <https://saref.etsi.org/saref4agri/>
                PREFIX s4city: <https://saref.etsi.org/saref4city/>
                PREFIX saref: <https://saref.etsi.org/core/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

                SELECT DISTINCT ?BUcadastralReference ?BUpolygon ?ADpoint (MAX(?KPIaValue) AS ?KPIaValueBUmax)
                WHERE{
                  ?CP a bigg:CadastralParcel;
                      geosp:sfContains ?BU;
                      vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                  ?BU a s4agri:Building;
                      rdfs:label ?BUcadastralReference;
                      geosp:hasGeometry/geosp:asWKT ?BUpolygon;
                      geosp:sfContains ?BS.
                  ?BS a s4agri:BuildingSpace;
                      rdfs:label ?BScadastralReference;
                      bigg:mainUse/skos:prefLabel "Residential".
                  ?KPIa a s4city:KeyPerformanceIndicatorAssessment;
                        s4city:quantifiesKPI/rdfs:label "Non renewable energy use intensity";
                        s4city:assesses ?BS;
                        saref:hasValue ?KPIaValue;
                        s4city:hasCreationDate ?KPIaDate.
                  {
                    SELECT DISTINCT ?CP WHERE{
                                ?CP a bigg:CadastralParcel;
                                    vcard:hasAddress/vcard:hasGeo/geosp:asWKT ?ADpoint.
                                FILTER (geof:sfWithin(?ADpoint, "%s"^^geosp:wktLiteral))
                            } 
                  }
                  FILTER (YEAR(?KPIaDate) = %s )
                } GROUP BY ?BUcadastralReference ?BUpolygon ?ADpoint
                """ % (wkt, year)
            db.setQuery(query)
            # Run query and store its results
            results = db.query().bindings
            df = pd.DataFrame()
            i = 1
            for result in results:
                row = pd.DataFrame({"index": i,
                                    "BUcadastralReference": [result["BUcadastralReference"].value],
                                    "BUpolygon": [result["BUpolygon"].value],
                                    "KPIaValueBUmax": [result["KPIaValueBUmax"].value],
                                    "ADpoint": [result["ADpoint"].value]
                                    }, index=[i])
                df = pd.concat([df, row])
                i += 1

            # Stop the chrono
            toc = time.time()
            # Generate the figure to be displayed
            fig = eb_heatmap.display_benchmarking(df,wkt)
    # Calculate the elapsed time
    took = round(toc - tic, 3)

    return render_template('dashboard/index.html', took=took, fig=fig, year=year)
