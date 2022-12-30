#!/bin/sh

set -e

export PYTHONDEVMODE=1

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

run mypy src
run pylint --rcfile=../../.pylintrc src tests
run python -m flake8 --select=DUO src  # Dlint
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pip-audit --strict --progress-spinner=off -r requirements/requirements-base.txt -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1
run safety check --bare -r requirements/requirements-base.txt -r requirements/requirements.txt -r requirements/requirements-dev.txt
run bandit --quiet --recursive src/
NAMES_TO_IGNORE='Anchore*,Axe*,AzureDevops*,Bandit*,Calendar*,Cloc*,Cobertura*,Composer*,CxSAST*,Gatling*,Generic*,GitLab*,Jacoco*,Jenkins*,Jira*,JMeter*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,SARIF*,Snyk*,SonarQube*,Trello*'
run vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py

