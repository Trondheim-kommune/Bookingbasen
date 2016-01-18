# -*- coding: utf-8 -*-
import base64
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import logging
from flask import current_app

from suds.client import Client
from suds.wsse import UsernameToken, Security
from domain.models import FesakSak, FesakJournalpost, Application

############################################################
## Utilities for creating the arkiv objects used by the WS #
############################################################

class WSHeader(object):
    '''
        All hardcoded values have been described as so by the client.
    '''

    def build(self):
        return {
                "AvsenderSystemkode": u"FLODB"
        }


class WSSak(object):
    '''
        All hardcoded values have been described as so by the client.
    '''

    def __init__(self, resource_name=None, saksansvarlig=None):
        '''
        Creates a datatransfer object suitable for generating a fesak sak.

        Parameters
        ----------
        lokale : String, name of the resource the sak is about
        saksansvarlig: String, Ident som er innlogget i FLOD
        '''
        self.tittel1 = (u'Langtidsleie av lokale ' + resource_name)
        self.saksansvarlig = saksansvarlig

    def build(self):
        return {
            "EksterntSaksnr": u"%s" % datetime.now().strftime('%Y/m%d%H%M%S%f'),
            "Tittel1": self.tittel1,
            "OrdningsprinsippKode": u"FE",
            "Ordningsverdi": u"614",
            "Ordningsbeskrivelse": u"Bygg, lokaler",
            "Arkivdel": u"EL-SAKARKI",
            "Saksansvarlig": self.saksansvarlig
        }


class WSJournalpost(object):
    '''
        All hardcoded values have been described as so by the client.
    '''

    def __init__(self, eksternt_saksnr=None, adressat1=None, saksbehandler=None, tittel1=None, tittel2=None,
                 dokument=None):
        '''
        Creates a datatransfer object suitable for generating a fesak_journalpost.

        Parameters
        ----------
        adressat1 : WSAdressat, søkerens adressat
        saksbehandler: String, Ident på innlogget bruker
        tittel1: String, søknad/vedtak om "XXXX" fra flod
        tittel2: String, navn på lånetaker
        dokument: WSDokument, dokument knyttet journalposten
        '''
        self.adressat1 = adressat1
        self.saksbehandler = saksbehandler
        self.tittel1 = tittel1
        self.tittel2 = tittel2
        self.dokument = dokument

    def build(self):
        return {
            "EksterntSaksnr": self.eksternt_saksnr,
            "Adressat1": self.adressat1.build(),
            "Saksbehandler": self.saksbehandler,
            "Tittel1": self.tittel1,
            "Tittel2": self.tittel2,
            "Dokument": self.dokument.build(),
            "ArkivKontekstReferanse": u"U"
        }


class WSAdressat(object):
    '''
        All hardcoded values have been described as so by the client.
    '''

    def __init__(self, fornavn=None, etternavn=None, adresse1=None, adresse2=None, postnr=None, sted=None,
                 foedselsnr=None, orgnr=None):
        '''
        Creates a datatransfer object suitable for generating a fesak adressat.

        Parameters
        ----------
        fornavn: String, Firmanavn eller fornavn på søker - merk er dette et firma skrives hele firmanavn i Fornavn
        etternavn: String, For organisasjoner benyttes kun Fornavn som navnefelt, Etternavn på søker
        adresse1: String, Adresse
        adresse2: String, Evnt adresselinje 2
        postnr: String, Postnr
        sted: String, poststed
        foedselsnr: String Fødselsnummer ddmmaasssss
        orgnr: String, Orgnummer (9 tegn)
        '''
        self.fornavn = fornavn
        self.etternavn = etternavn
        self.adresse1 = adresse1
        self.adresse2 = adresse2
        self.postnr = postnr
        self.sted = sted
        self.foedselsnr = foedselsnr
        self.orgnr = orgnr

    def build(self):
        return {
            "Fornavn": self.fornavn,
            "Etternavn": self.etternavn,
            "Adresse1": self.adresse1,
            "Adresse2": self.adresse2,
            "Postnr": self.postnr,
            "Sted": self.sted,
            "Landkode": u"NO",
            "Foedselsnr": self.foedselsnr,
            "Orgnr": self.orgnr
        }


class WSDokument(object):
    '''
        All hardcoded values have been described as so by the client.
    '''

    def __init__(self, dokument_tittel, fil_innhold):
        '''
        Creates a datatransfer object suitable for generating a journalpost dokument.

        Parameters
        ----------
        dokumentTittel: String, obligatorisk, string, (Bør settes når det er mer enn 1 dok)
        filInnhold": String, has to be base64 encoded
        '''
        self.dokument_tittel = dokument_tittel
        self.fil_innhold = fil_innhold

    def build(self):
        return {
            "DokumentTittel": self.dokument_tittel,
            "FilInnhold": self.fil_innhold,
        }


###################
## Arkiv clients  #
###################

class ArkivClient(object):
    '''
    Proxy for the clients, this class will handle errors.
    '''
    def __init__(self, app, url, user, password):
        try:
            self.arkiv_ws_client = ArkivWSClient(app, url, user, password)
        except Exception:
            raise Exception('Could not create Arkiv WS client.')

    def ny_sak(self, application_id, ws_sak):
        response = self.arkiv_ws_client.ny_sak(application_id, ws_sak)
        print "Status:%s, melding:%s" % (response.status, response.melding)
        if response.status != "200":
            raise ValueError('Response ikke ok! %s' % response)

    def ny_journalpost(self, application_id, ws_journalpost):
        response = self.arkiv_ws_client.ny_journalpost(application_id, ws_journalpost)
        print "Status:%s, melding:%s" % (response.status, response.melding)
        if response.status != "200":
            raise ValueError('Response ikke ok! %s' % response)


class AbstractArkivClient(object):
    def ny_sak(self, application_id, ws_sak):
        raise NotImplemented("This method has to be implemented by the subclasses of AbstractArkivClient")

    def ny_journalpost(self, application_id, ws_sak):
        raise NotImplemented("This method has to be implemented by the subclasses of AbstractArkivClient")



# DB versjonen av ArkivClient, kan fjernes når ny versjon av FeSak kommer på plass
class ArkivDBClient(AbstractArkivClient):
    def __init__(self, app):
        self.app = app

    def ny_sak(self, application_id, ws_sak):
        application = self.app.db_session.query(Application).filter(Application.id == application_id).one()
        sakdata_build = ws_sak.build()
        fesak_sak = FesakSak(application, sakdata_build["EksterntSaksnr"], json.dumps(WSHeader().build()), json.dumps(sakdata_build))

        self.app.db_session.add(fesak_sak)
        self.app.db_session.commit()

        return fesak_sak

    def ny_journalpost(self, application_id, ws_journalpost):
        fesak_sak = self.app.db_session.query(FesakSak).filter(FesakSak.application_id == application_id).one()
        ws_journalpost.eksternt_saksnr = fesak_sak.saksnummer
        fesak_journalpost = FesakJournalpost(fesak_sak, json.dumps(WSHeader().build()),
                                             json.dumps(ws_journalpost.build()))

        self.app.db_session.add(fesak_journalpost)
        self.app.db_session.commit()

        return fesak_journalpost


# WS versjonen av ArkivClient, ikke i bruk før FeSak kommer på plass
class ArkivWSClient(ArkivDBClient):
    ARKIVSAK_WSDL = '/T10121_ArkivSak/ProxyServices/ArkivSak?wsdl'
    JOURNALPOSTERING_WSDL = '/T10122_Journalpostering/ProxyServices/Journalpostering?wsdl'

    def __init__(self, app, url, user, password):
        super(ArkivWSClient, self).__init__(app)
        if not url:
            raise Exception('Could not create Arkiv WS Client: ARKIV_URL empty')
        if not user:
            raise Exception('Could not create Arkiv WS Client: ARKIV_USER empty')
        if not password:
            raise Exception('Could not create Arkiv WS Client: ARKIV_PASSWORD empty')

        arkivsak_url = url + self.ARKIVSAK_WSDL
        journalpostering_url = url + self.JOURNALPOSTERING_WSDL
        base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
        authenticationHeader = {
            "Authorization": "Basic %s" % base64string
        }
        try:
            from suds.transport.http import HttpAuthenticated
            self.sak_client = Client(arkivsak_url, transport=HttpAuthenticated(username=user, password=password))
            self.journalpostering_client = Client(journalpostering_url, transport=HttpAuthenticated(username=user, password=password))
        except Exception, e:
            raise Exception('SUDS client initialisation failed.')

    def ny_sak(self, application_id, ws_sak):
        # Saksnummer has to be saved because it will be needed when creating journalposts
        super(ArkivWSClient, self).ny_sak(application_id, ws_sak)
        return self.sak_client.service.T10121_ArkivSak(header=WSHeader().build(),
                                                       operasjon="Ny",
                                                       sak=ws_sak.build()
        )

    def ny_journalpost(self, application_id, ws_journalpost):
        # getting the saksnumer from the FesakSak table
        fesak_sak = self.app.db_session.query(FesakSak).filter(FesakSak.application_id == application_id).one()
        ws_journalpost.eksternt_saksnr = fesak_sak.saksnummer
        return self.journalpostering_client.service.T10122_JournalPostering(header=WSHeader().build(),
                                                                            journalpostering=ws_journalpost)


# videreutvikles/tas i bruk når vi integrerer mot FeSak
class BaseWSResponseHandler(object):
    def __init__(self, response):
        if response is None:
            raise ValueError('Response is None')
        try:
            self.status = response.status
            self.melding = response.melding
        except Exception:
            raise ValueError('Invalid response')

    def get_text_value_for_xpath(self, xpath, concatstring=' ', startnode=None):
        if not xpath:
            return ''
        if startnode is None:
            startnode = self.ws_response_etree
        matches = startnode.findall(xpath)
        values = [match.text.strip() for match in matches if match.text]
        return concatstring.join(values)


class SakWSResponseHandler(BaseWSResponseHandler):
    def __init__(self, response):
        super(BaseWSResponseHandler, self).__init__(response)
        try:
            self.returSaksnr = response.returSaksnr
        except Exception:
            raise ValueError('Invalid response')
