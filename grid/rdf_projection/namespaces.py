from rdflib import Namespace

DEFAULT_GRID_URI = "https://grid.example/ns/"

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("https://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

BUILTIN_PREFIXES: dict[str, str] = {
    "rdf": str(RDF),
    "skos": str(SKOS),
    "schema": str(SCHEMA),
    "dcterms": str(DCTERMS),
    "rdfs": str(RDFS),
    "xsd": str(XSD),
}
