#!/bin/sh
# clean on steroids: the venv gets wipe out as well!
###

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

## running clean
. project-clean.sh

# virtualenv deletion
###
venvDir="venv"
if [ -d "$venvDir" ]
then
	echo "Virtualenv directory '`pwd`/$venvDir' found, deleting it."
	rm -rfv ${venvDir}
else
    echo "No virtualenv directory '`pwd`/$venvDir' to delete."
fi

