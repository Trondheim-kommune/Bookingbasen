#!/bin/sh
export SONAR_RUNNER_HOME=/opt/sonar-runner-2.2
export PATH=$PATH:${SONAR_RUNNER_HOME}/bin
echo -e "******************************"
echo -e "Build environment"
echo -e "******************************"
export AUTH_DATABASE_URL=postgres://jenkins:jenkins@javaci.bouvet.no:5432/test_flod_auth
export AUTH_ADMIN_USER_ID=FlodSuperUser
env
python --version
pip --version
virtualenv --version
uname -a
lsb_release -a
echo -e "******************************"
echo "Building project in \$WORKSPACE"
echo -e "******************************"
cd ${WORKSPACE} && \
    bash project-reset.sh && \
    bash project-init.sh && \
    bash project-test.sh && \
    bash project-test-with-coverage.sh
