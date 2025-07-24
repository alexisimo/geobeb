# GEOBEB
[GEOBEB](https://github.com/alexisimo/geobeb) (GEOgraphically aggregated Building Energy Benchmarking) is a linked data exploitation app created for the [BIGG](https://www.bigg-project.eu/) (Building Information aGGregation,
harmonization and analytics platform) knowledge graph.

## Usage
This is a Flask web application that runs on top of a SPARQL endpoint by quering linked data generated following the [BIGGstd ontology in its 1.1 version.](https://github.com/biggproject/Ontology/tree/v1.1/BIGGstd)

To run the application make sure you meet the libraries `requirements.txt`, navigate to the project directory and run the command: 
```bash
flask --app geobeb run
```
---
The application doesn't provide with any data. The SPARQL endpoint's port is by default 7200.

## Data
You can use this app on top of the Cross-sectional Buildings Energy Benchmarking Knowledge Graph dataset, generated using [this pipeline](https://github.com/alexisimo/BIGG-KG-Pipeline) and published in [this Zenodo](https://doi.org/10.5281/zenodo.13943296).

## Citation
This app was developed to demonstrate the exploitation phase of the research article Linked Data Generation Methodology and the Geospatial Cross-Sectional Buildings Energy Benchmarking Use Case.
```bib
@article{Martinez2024,
   author = {Edgar A. Martínez-Sarmiento and Jose Manuel Broto and Eloi Gabaldon and Jordi Cipriano and Roberto García and Stoyan Danov and Edgar A Martinez-Sarmiento and Jose Manuel Broto and Eloi Gabaldon and Jordi Cipriano and Roberto Garcia and Stoyan Danov},
   doi = {10.3390/en17123006},
   issue = {12},
   journal = {ENERGIES},
   keywords = {energy benchmarking,linked data,semantic web},
   month = {6},
   pages = {1-24},
   title = {Linked Data Generation Methodology and the Geospatial Cross-Sectional Buildings Energy Benchmarking Use Case},
   volume = {17},
   year = {2024}
}
```

### Aknowledgment
 [BIGG](https://www.bigg-project.eu/) knowledge graph was part of an H2020 project founded by the European Union Grant Agreement N. 957047

The WKT polygon drawing feature was adapted from the [OpenstreetMap WKT Playground github repository](https://github.com/clydedacruz/openstreetmap-wkt-playground) implemented by [@clydedcruz](https://github.com/clydedcruz).
