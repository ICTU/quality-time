import React from 'react';
import { Image } from 'semantic-ui-react';

import AzureDevops from './azure_devops.png';
import Gitlab from './gitlab.png';
import HQ from './hq.png';
import JaCoCo from './jacoco.png';
import Jenkins from './jenkins.png';
import Jira from './jira.png';
import Junit from './junit.png';
import OpenVAS from './openvas.png';
import OWASPDependencyCheck from './owasp_dependency_check.png';
import OWASPZAP from './owasp_zap.png';
import RobotFramework from './robot_framework.png';
import Sonarqube from './sonarqube.png';
import Wekan from './wekan.png';

function Logo(props) {
    const logo = {
        azure_devops: AzureDevops,
        gitlab: Gitlab,
        hq: HQ,
        jacoco: JaCoCo,
        jenkins: Jenkins,
        jira: Jira,
        junit: Junit,
        openvas: OpenVAS,
        owasp_dependency_check: OWASPDependencyCheck,
        owasp_zap: OWASPZAP,
        robot_framework: RobotFramework,
        sonarqube: Sonarqube,
        wekan: Wekan
    }[props.logo];
    return (
        logo ? <Image src={logo} alt={`${props.alt} logo`} size="mini" spaced="right" /> : null
    )
}

export { Logo }
