#!/usr/bin/env/python
# -*- coding: utf-8 -*-


class ErvCode(object):

    def __str__(self):
        return ''.join((self.kommunenr, self.oppdragsgiver, self.kortart,
                        self.aar, self.lopenummer, self.varenummer,
                        self.linjenummer, self.varenavn, self.grunnlag,
                        self.pris, self.utregnet, self.fra_til_dato,
                        self.kontonummer, self.momskode))


def erv_organisation(application, invoice_amount, org_number):
    e = _erv(application, invoice_amount)

    # 5. Løpenummer (length: 15)
    # 4000 indicates organisation number
    e.lopenummer = '4000' + org_number.zfill(11)
    return e


def erv_person(application, invoice_amount, nin):
    e = _erv(application, invoice_amount)
    # 5. Løpenummer (length: 15)
    # 1000 indicates national identity number
    e.lopenummer = '1000' + nin
    return e


def _erv(application, invoice_amount):
    e = ErvCode()
    # 1. Kommunenummer (length: 4)
    # Constant, specified by TRK
    e.kommunenr = '1601'

    # 2. Oppdragsgiver (length: 2)
    # Constant, specified by TRK
    e.oppdragsgiver = '22'

    # 3. Kortart (length: 2)
    # Constant
    e.kortart = '50'

    # 4. År (length: 2)
    # Invoice year, without century: 2014 -> 14
    e.aar = application.application_time.strftime('%y')

    # 6. Varenummer (length: 3)
    # Generate own
    e.varenummer = '100'

    # 7. Linjenummer (length: 1)
    # Constant
    e.linjenummer = '0'

    # 8. Varenavn (length: 17)
    # Not used, blank
    e.varenavn = ' ' * 17

    # 9. Grunnlag/beløp (length: 9)
    # Invoice amount in cents, leftpadded with zeros
    e.grunnlag = '{0:07d}00'.format(invoice_amount)

    # 10. Pris (length: 7)
    # Not used, blank
    e.pris = ' ' * 7

    # 11. Utregnet (length: 1)
    # Constant, 'X' indicates that 'grunnlag' specifies the amount
    e.utregnet = 'X'

    # 12. Fra-Til dato (length: 8)
    # Not used, blank
    e.fra_til_dato = ' ' * 8

    # 13. Kontonummer (length: 8)
    e.kontonummer = ' ' * 8

    # 14. Momskode (length: 1)
    e.momskode = ' '
    return e
