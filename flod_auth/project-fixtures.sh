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

# virtualenv check
###
venvDir="venv"
if [ -d "$venvDir" ]
then
	echo "Virtualenv directory '`pwd`/$venvDir' found."
else

    echo "Virtualenv directory '`pwd`/$venvDir' not found, run the project-init.sh script."
    exit -1
fi

. venv/bin/activate

# pass environment variables to subsequent shell
###
set -a

# source .shell-env if found.
###
if [ -f ".shell-env" ]
then
	echo "Found '.shell-env' file, sourcing it..."
	. .shell-env
fi

## update the python path
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${BASEDIR}/src/main/:${PYTHONPATH}
echo "PYTHONPATH=$PYTHONPATH"

# run db_dump
###
CMD="python manage.py fixtures"
echo "Executing command '$CMD'"

`${CMD}`
