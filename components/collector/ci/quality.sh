#!/bin/sh

set -e

mypy src
pylint src tests
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
NAMES_TO_IGNORE='Anchore*,AxeCSV*,AzureDevops*,Bandit*,Calendar*,Cloc*,Cobertura*,Composer*,CxSAST*,GitLab*,HQ*,Jacoco*,Jenkins*,Jira*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,SonarQube*,Trello*,Wekan*'
vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_white_list.py

