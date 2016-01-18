Flod Matrikkel RestAPI
======================


A rather lightweight REST API on top of the SOAP-api to Matrikkelen. Supports the use-cases for
Flod, i.e. look up addresses and buildings.

Endpoints
---------

### Addresses

- /api/{VERSION}/addresses?query=MY_QUERY

The query can be of type "Vegen", "Vegen 6" or "Vegen 6A", calls the "findAdresserForVeg()" method in
AdresseWebService and extracts relevant information, thus returing a list of objects on the form:

    {
        "name": "Vegen 6 A",
        "matrikkel_ident": {"kommunenr": "nnnn", "gardsnr": n, "bruksnr": n, "festenr": m, "seksjonsnr": n}
    }
where festenr and seksjonsnr is optional.

The name is composed of the attributes "adressenavn" from Adresse and the "nr"
(and optionally "bokstav") from "vegadresseIdent".

The matrikkel_ident is composed of the "kommunenr", "gardsnr", "bruksnr" and
optionally "festenr" and "seksjonsnr" from the "matrikkelenhetIdent"


###Buildings

- /api/{VERSION}/addresses?gardsnr=GARDSNR&bruksnr=BRUKSNR&festenr=FESTENR&seksjonsnr=SEKSJONSNR

where "festenr" and "seksjonsnr" is optional.

This calls the "findBygningerForMatrikkelenhet()" in BygningWebService and picks out location and
building number from the response (after filtering out "BygningsEndring" objects). This returns a
list of objects on the form:

    {
        "position": {
            "lon": longitude in epsg:4326,
            "lat": latitude in epsg:4326
        },
        "building_number": nnnnnnn
    }

The "position" is derived from the "representasjonspunkt" of the building (i.e. parsed and split).
The SOAP requests sets the SOSI-code 84 in the MatrikkelContext in the request (i.e. EPSG: 4326)

The "building_number" is the "bygningsnr" attribute from the "bygningIdent" of the "Bygning"