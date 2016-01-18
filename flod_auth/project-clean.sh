#!/bin/sh
# Cleans the project, but keeps the venv
########################################

# The script expects to be running for where it is saved
###
CURRENTDIR=`pwd`
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "$CURRENTDIR" != "$BASEDIR" ]
then
    cd ${BASEDIR}
	echo "Changed current catalog to '$BASEDIR'."
else
	echo "Already in $CURRENTDIR, not changing catalog."
fi

# coverage files deletion
###
coverageXML="coverage.xml"
nosetestsXML="nosetests.xml"
coverageDIR=".coverage"

if [ -f "$coverageXML" ]
then
    echo "Deleting $coverageXML..."
    rm -v ${coverageXML}
fi
if [ -f "$nosetestsXML" ]
then
    echo "Deleting $nosetestsXML..."
    rm -v ${nosetestsXML}
fi
if [ -d "$coverageDIR" ]
then
    echo "Deleting $coverageDIR..."
    rm ${coverageDIR}
    rm -vrf ${coverageDIR}
fi
echo "Coverage files deleted."

# pyc files deletion
###
find . -path "*venv" -prune -o -name "*pyc" | grep -v "venv" | xargs rm -v

echo "pyc files deleted."
