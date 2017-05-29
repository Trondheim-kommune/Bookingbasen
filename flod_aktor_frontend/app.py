# -*- coding: utf-8 -*-
import os
from logging import StreamHandler, INFO

from flod_aktor_frontend import app


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

if not app.debug:
    stream_handler = StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(INFO)
