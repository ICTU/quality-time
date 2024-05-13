#!/bin/bash

source ../../ci/base.sh

# Ruff
run pipx run `spec ruff` check .
run pipx run `spec ruff` format --check .

# Mypy
run pipx run `spec mypy` --python-executable=$(which python) src tests

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
# See https://github.com/aio-libs/aiohttp/issues/6772 for why we ignore the CVE
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
# Vulnerability ID: 67599
# ADVISORY: ** DISPUTED ** An issue was discovered in pip (all versions) because it installs the version with the
# highest version number, even if the user had intended to obtain a private package from a private index. This only
# affects use of the --extra-index-url option, and exploitation requires that the...
# CVE-2018-20225
# For more information about this vulnerability, visit https://data.safetycli.com/v/67599/97c
run pipx run `spec safety` check --bare --ignore 67599 -r requirements/requirements.txt -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
NAMES_TO_IGNORE='Anchore*,Axe*,AzureDevops*,Bandit*,Calendar*,CargoAudit*,Cloc*,Cobertura*,Composer*,CxSAST*,DependencyTrack*,Gatling*,Generic*,GitLab*,Harbor*,Jacoco*,Jenkins*,Jira*,JMeter*,JUnit*,ManualNumber*,NCover*,Npm*,OJAudit*,OpenVAS*,OWASPDependencyCheck*,OWASPZAP*,PerformanceTestRunner*,Pip*,PyupioSafety*,QualityTime*,RobotFramework*,SARIF*,Snyk*,SonarQube*,Trello*,TrivyJSON*'
run pipx run `spec vulture` --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py
