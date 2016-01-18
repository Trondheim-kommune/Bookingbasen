#!/bin/sh

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

if [ -f ".shell-env" ]
then
	echo "Found '.shell-env' file, sourcing it..."
	. .shell-env
fi

# virtualenv creation
###
venvDir="venv"
if [ -d "$venvDir" ]
then
	echo "Virtualenv directory '`pwd`/$venvDir' found."
else
    virtualenv ${venvDir}
    echo "Virtualenv directory '`pwd`/$venvDir' created."
fi

. venv/bin/activate

# pip install
###
pip install --upgrade --allow-external argparse -r requirements.txt

