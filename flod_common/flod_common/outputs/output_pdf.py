# -*- coding: utf-8 -*-
from xhtml2pdf import pisa
from StringIO import StringIO
from datetime import datetime
from flask import render_template, Response
from flod_common.outputs.default_css import DEFAULT_CSS


def create_pdf(pdf_data):
    pdf = StringIO()
    pisa.CreatePDF(StringIO(pdf_data), pdf, quiet=False, default_css=DEFAULT_CSS)
    return pdf


def output_pdf(data, code, template=None, headers=None):
    if not template:
        raise Exception("Template missing")
    message = render_template(template, **data)
    pdf = create_pdf(message)
    response = Response(response=pdf.getvalue(), status=code)
    response.headers.extend(headers or {})
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="eksport-' + datetime.today().isoformat() + '.pdf"'
    return response
