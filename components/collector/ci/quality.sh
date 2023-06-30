#!/bin/bash

source ../../ci/base.sh

# Ruff
run pipx run `spec ruff` .

# Mypy
run pipx run `spec mypy` --python-executable=$(which python) src tests

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
run pipx run `spec safety` check --bare -r requirements/requirements.txt -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
NAMES_TO_IGNORE='Anchore*,Axe*,AzureDevops*,Bandit*,Calendar*,CargoAudit*,Cloc*,Cobertura*,Composer*,CxSAST*,Gatling*,Generic*,GitLab*,Harbor*,Jacoco*,Jenkins*,Jira*,JMeter*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,SARIF*,Snyk*,SonarQube*,Trello*'
run pipx run `spec vulture` --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py

# Black
run pipx run `spec black` --check src tests
