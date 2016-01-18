#!/bin/sh
# runs the alembic migrations
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

# virtualenv check
###
venvDir="venv"
if [ -d "$venvDir" ]
then
	echo "Virtualenv directory '`pwd`/$venvDir' found."
else

    echo "Virtualenv directory '`pwd`/$venvDir' not found, create one and rerun this script!"
    exit -1
fi

. venv/bin/activate

set -a

if [ -f ".shell-env" ]
then
	echo "Found '.env' file, sourcing it..."
	. .env
fi

## update the python path
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${BASEDIR}:${PYTHONPATH}
echo "PYTHONPATH=$PYTHONPATH"

# runs the migrations for prod
###
CMD="alembic -c alembic.ini $*"
echo "Executing command '$CMD'"

exec ${CMD}
