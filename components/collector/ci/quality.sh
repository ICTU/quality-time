#!/bin/sh

set -e

mypy src
pylint src
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
NAMES_TO_IGNORE='AxeCSV*,AzureDevops*,Bandit*,Calendar*,CxSAST*,Gitlab*,HQ*,Jacoco*,Jenkins*,Jira*,JUnit*,ManualNumber*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,PyupioSafety*,QualityTime*,RobotFramework*,SonarQube*,Trello*,Wekan*'
vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/
