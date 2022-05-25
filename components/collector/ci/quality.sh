#!/bin/sh

set -e

# We currently get one warning when running Python in dev mode:
# astroid/node_classes.py:90: DeprecationWarning: The 'astroid.node_classes' module is deprecated and will be replaced
# by 'astroid.nodes' in astroid 3.0.0
# Turn off dev mode until astroid gets fixed or there's a way to suppress warnings in third party code
#export PYTHONDEVMODE=1

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

run mypy src
run pylint --rcfile=../../.pylintrc src tests
run python -m flake8 --select=DUO src  # Dlint
run pip-audit --strict --progress-spinner=off -r requirements/requirements-base.txt -r requirements/requirements.txt -r requirements/requirements-dev.txt
run safety check --bare --ignore 41002 -r requirements/requirements-base.txt -r requirements/requirements.txt -r requirements/requirements-dev.txt  # See https://github.com/nedbat/coveragepy/issues/1200
run bandit --quiet --recursive src/
NAMES_TO_IGNORE='Anchore*,Axe*,AzureDevops*,Bandit*,Calendar*,Cloc*,Cobertura*,Composer*,CxSAST*,Gatling*,Generic*,GitLab*,Jacoco*,Jenkins*,Jira*,JMeter*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,SARIF*,Snyk*,SonarQube*,Trello*'
run vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py
