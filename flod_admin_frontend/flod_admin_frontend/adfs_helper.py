#!/usr/bin/env python
# -*- coding: utf-8 -*-


def parse_claims(document):
    ns = {'samlp': 'urn:oasis:names:tc:SAML:2.0:assertion'}
    expression = ('//samlp:Attribute'
                  '[@Name="http://schemas.xmlsoap.org/claims/Group"]'
                  '/samlp:AttributeValue')
    claims_values = document.xpath(expression, namespaces=ns)
    return [el.text for el in claims_values]


def find_cn(dn):
    cnames = [cn.partition('=')[2] for cn in dn.split(',')
              if cn.startswith('CN=')]
    if len(cnames) > 0:
        return cnames[0]
    return None


def extract_roles(claims):
    return [cn for cn in (find_cn(dn) for dn in claims)
            if cn is not None]
