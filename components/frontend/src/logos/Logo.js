import React from 'react';
import { Image } from 'semantic-ui-react';

import Anchore from './anchore.png';
import Axe from './axe.png';
import AzureDevops from './azure_devops.png';
import Bandit from './bandit.png';
import Composer from './composer.png';
import Checkmarx from './checkmarx.png';
import Gitlab from './gitlab.png';
import JaCoCo from './jacoco.png';
import Jenkins from './jenkins.png';
import Jira from './jira.png';
import Junit from './junit.png';
import NCover from './ncover.png';
import OpenVAS from './openvas.png';
import OWASPDependencyCheck from './owasp_dependency_check.png';
import OWASPDependencyCheckJenkinsPlugin from './owasp_dependency_check_jenkins_plugin.png';
import OWASPZAP from './owasp_zap.png';
import Python from './python.png';
import Pyupio from './pyupio.png';
import QualityTime from './quality_time.png';
import RobotFramework from './robot_framework.png';
import Sonarqube from './sonarqube.png';
import Trello from './trello.png';
import Wekan from './wekan.png';

export function Logo(props) {
    const logo = {
        anchore: Anchore,
        axecsv: Axe,
        azure_devops: AzureDevops,
        bandit: Bandit,
        composer: Composer,
        cxsast: Checkmarx,
        gitlab: Gitlab,
        jacoco: JaCoCo,
        jacoco_jenkins_plugin: JaCoCo,
        jenkins: Jenkins,
        jenkins_test_report: Jenkins,
        jira: Jira,
        junit: Junit,
        ncover: NCover,
        openvas: OpenVAS,
        owasp_dependency_check: OWASPDependencyCheck,
        owasp_dependency_check_jenkins_plugin: OWASPDependencyCheckJenkinsPlugin,
        owasp_zap: OWASPZAP,
        pip: Python,
        pyupio_safety: Pyupio,
        quality_time: QualityTime,
        robot_framework: RobotFramework,
        sonarqube: Sonarqube,
        trello: Trello,
        wekan: Wekan
    }[props.logo];
    return (
        logo ? <Image src={logo} alt={`${props.alt} logo`} size="mini" spaced="right" /> : null
    )
}
