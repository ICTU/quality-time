import React from 'react';
import { Image } from 'semantic-ui-react';

import AzureDevops from './azure_devops.png';
import Bandit from './bandit.png'
import Checkmarx from './checkmarx.png';
import Gitlab from './gitlab.png';
import HQ from './hq.png';
import JaCoCo from './jacoco.png';
import Jenkins from './jenkins.png';
import Jira from './jira.png';
import Junit from './junit.png';
import OpenVAS from './openvas.png';
import OWASPDependencyCheck from './owasp_dependency_check.png';
import OWASPDependencyCheckJenkinsPlugin from './owasp_dependency_check_jenkins_plugin.png';
import OWASPZAP from './owasp_zap.png';
import Pyupio from './pyupio.png';
import RobotFramework from './robot_framework.png';
import Sonarqube from './sonarqube.png';
import Trello from './trello.png';
import Wekan from './wekan.png';

export function Logo(props) {
    const logo = {
        azure_devops: AzureDevops,
        bandit: Bandit,
        cxsast: Checkmarx,
        gitlab: Gitlab,
        hq: HQ,
        jacoco: JaCoCo,
        jenkins: Jenkins,
        jira: Jira,
        junit: Junit,
        openvas: OpenVAS,
        owasp_dependency_check: OWASPDependencyCheck,
        owasp_dependency_check_jenkins_plugin: OWASPDependencyCheckJenkinsPlugin,
        owasp_zap: OWASPZAP,
        pyupio_safety: Pyupio,
        robot_framework: RobotFramework,
        sonarqube: Sonarqube,
        trello: Trello,
        wekan: Wekan
    }[props.logo];
    return (
        logo ? <Image src={logo} alt={`${props.alt} logo`} size="mini" spaced="right" /> : null
    )
}
