#!/bin/sh

set -e

mypy src
# Turn off Pylint until it works with Python 3.9. In the mean time we run a separate GitHub Action for Pylint with
# Python 3.8, see .github/workflows/pylint.yml
# pylint src tests
isort **/*.py --check-only
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
NAMES_TO_IGNORE='Anchore*,Axe*,AzureDevops*,Bandit*,Calendar*,Cloc*,Cobertura*,Composer*,CxSAST*,Generic*,GitLab*,Jacoco*,Jenkins*,Jira*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,Snyk*,SonarQube*,Trello*,Wekan*'
vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py

