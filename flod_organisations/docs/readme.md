1. sphinx requirement i requirements.txt
2. jeg har brukt følgende ressurser:

https://pythonhosted.org/sphinxcontrib-httpdomain/
http://pythonhosted.org/sphinxcontrib-httpdomain/#module-sphinxcontrib.autohttp.flask
http://sphinx-doc.org/tutorial.html
https://pythonhosted.org/an_example_pypi_project/sphinx.html
    http://codeandchaos.wordpress.com/2012/07/30/sphinx-autodoc-tutorial-for-dummies/
    http://raxcloud.blogspot.no/2013/02/documenting-python-code-using-sphinx.html

den siste viste seg å være bra.


3. installer sphinx med requirments.txt
4. last ned extensions fra https://bitbucket.org/birkenfeld/sphinx-contrib (hg clone)
jeg la det i dir sphinx_extensions i flod_organisations. spiller ikke noen rolle iom at vi må
installere de på et vis...
se i readme, men jeg installerte extensionene med:
cd dir
python setup.py build
python setup.py install

fra: https://bitbucket.org/birkenfeld/sphinx-contrib/src/743c75df66d78e0e2589e0bd35dc609ab6ab9077/httpdomain/?at=default

kjør:

sphinx-apidoc -A "martin polden" -F -o docs .

== legg docfiler i docs dir, kildekode er i current dir

index.rst og conf.py genereres bl.a. i docs/ de må editeres manuelt

enter index.rst:

den skal ha generert en lang liste over moduler...
kan evnt endre maxdepth fra 2 til 4 som jeg gjorde..

videre for at flask ext skalf unke må følgende legges til:

.. autoflask:: app:app                                                                       │ 23 fra: https://bitbucket.org/birkenfeld/sphinx-contrib/src/743c75df66d78e0e2589e0bd35dc6
   :endpoints:                                                                               │ 24                                                                                 
   :include-empty-docstring: 

som tar alle endpoints, selvom doc mangler. se doc for autoflask

i conf.py bør path til sourcecode settes tenker jeg; /vagrant/organisations/

vi legger  i tillegg til de 2 extensionene som er der fra før så legger vi til
'sphinxcontrib.autohttp.flask'

og så er det evnt. 100 flere configer du kan sette :)

en make fil skal ha blit generert; for å generere html kode:

make html

html finnes da i docs/_build/index.html

har problem at en del ressurser kommer opp dobbelt..usikker hvorfor

_build må slettes mellom hver makefor ikke å lage dobbelt opp og for at ting skal tre i effekt.
burde sikkert slette _build på generell basis da...vet ikke om det gir poeng i å sjekke inn
doccen men heller generere den når den trengs...?


