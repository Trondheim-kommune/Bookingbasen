Bookingbasen (og Aktørbasen)
================================

Dette er kildekoden bak Bookingbasen og Aktørbasen til Trondheim Kommune (TK)

TK tar i utgangspunktet ikke imot pull requests (forslag til endringer eller ny funksjonalitet) via GitHub.
TK kan derimot kontaktes via _digitalt punktum forstevalg alfakrøll trondheim punktum kommune punktum no_
TK vil kun innlemme forslag til endringer etc. i koden om TK finner dette hensiktsmessig.

Les mer om Bookingbasen [her](http://www.trondheim.kommune.no/content/1117741288/Bookingbasen---sok-om-lan-av-lokale)
eller besøke [her](https://booking.trondheim.kommune.no/)

Bookingbasen består av en rekke mikrotjenester som helt eller delvis deles med Aktørbasen og Tilskuddsbasen.
Tjenestene bookingbasen benytter seg av som er publisert her er:
* Autentisering (flod_auth)
* Booking (flod_booking)
* Fasiliteter (flod_facilities_backend)
* Matrikkel (flod_matrikkel_address_restapi)
* Organisasjoner (flod_organisations)

Frontend som bruker disse tjenestene via REST API er portalen (flod_admin_frontend og flod_frontend)
I tillegg brukes flod_calendar for Kalendervisning.

Aktørbasen er også en del av koden (i katalogen flod_aktor_frontend), som du kan lese mer om [her](http://www.trondheim.kommune.no/aktorbasen/)
og besøke [her](https://organisasjoner.trondheim.kommune.no/)

Aktørbasen er hovedsaklig en frontend (flod_aktor_frontend), og benytter seg av mikrotjenestene:
* Autentisering
* Organisasjoner

flod_common er delt kode mellom Tilskuddsbasen, Aktørbasen og Bookingbasen.
