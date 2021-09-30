import React from 'react';
import { Container, Divider, Grid, Header, Icon, Image, List, Segment } from 'semantic-ui-react';

function FooterItem({ children, icon, url }) {
    const item = icon ? <><Icon name={icon} /> {children}</> : children;
    return url ? <List.Item as="a" href={url}>{item}</List.Item> : <List.Item>{item}</List.Item>;
}

function FooterColumn({ children, header, textAlign, width }) {
    return (
        <Grid.Column width={width} textAlign={textAlign}>
            <Header inverted as='h4'>{header || <>&zwnj;</>}</Header>
            <List inverted link>
                {children}
            </List>
        </Grid.Column>
    )
}

function FooterCenterColumn({ header, children }) {
    return (
        <FooterColumn header={header} width={8} textAlign="center">
            {children}
        </FooterColumn>
    )
}

function FooterSideColumn({ header, children }) {
    return (
        <FooterColumn header={header} width={3} textAlign="left">
            {children}
        </FooterColumn>
    )
}


function AboutAppColumn() {
    return (
        <FooterSideColumn header={<><em>Quality-time</em> v{process.env.REACT_APP_VERSION}</>} >
            <FooterItem icon="flask" url="https://www.ictu.nl/about-us">Created by ICTU</FooterItem>
            <FooterItem icon="copyright outline" url="https://github.com/ICTU/quality-time/blob/master/LICENSE">License</FooterItem>
            <FooterItem icon="history" url={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/changelog.html`}>Changelog</FooterItem>
            <FooterItem icon="code branch" url="https://github.com/ICTU/quality-time">Source code</FooterItem>
        </FooterSideColumn>
    )
}

function SupportColumn() {
    return (
        <FooterSideColumn header="Support">
            <FooterItem icon="book" url={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/`}>Documentation</FooterItem>
            <FooterItem icon="user outline" url={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/usage.html`}>User manual</FooterItem>
            <FooterItem icon="bug" url="https://github.com/ICTU/quality-time/issues">Known issues</FooterItem>
            <FooterItem icon="comment outline" url="https://github.com/ICTU/quality-time/issues/new">Report an issue</FooterItem>
        </FooterSideColumn>
    )
}

function AboutReportColumn({ report, last_update }) {
    return (
        <FooterCenterColumn header="About this report">
            <FooterItem url={window.location.href}>{report.title}</FooterItem>
            <FooterItem>{report.subtitle}</FooterItem>
            <FooterItem>{last_update.toLocaleDateString()}</FooterItem>
            <FooterItem>{last_update.toLocaleTimeString()}</FooterItem>
        </FooterCenterColumn>
    )
}

function QuoteColumn() {
    return (
        <FooterCenterColumn>
            <FooterItem><em>Quality without results is pointless.</em></FooterItem>
            <FooterItem><em>Results without quality is boring.</em></FooterItem>
            <FooterItem>Johan Cruyff</FooterItem>
        </FooterCenterColumn>
    )
}

export function Footer({ report, last_update }) {
    return (
        <Segment inverted style={{ margin: '5em 0em 0em', padding: '5em 0em 3em' }}>
            <Container>
                <Grid>
                    <Grid.Row>
                        <Grid.Column width={1} />
                        <AboutAppColumn />
                        {report ? <AboutReportColumn report={report} last_update={last_update} /> : <QuoteColumn />}
                        <Grid.Column width={1} />
                        <SupportColumn />
                    </Grid.Row>
                </Grid>
                <Divider inverted section />
                <Image centered size='mini' src='./favicon.ico' />
            </Container>
        </Segment>
    )
}
