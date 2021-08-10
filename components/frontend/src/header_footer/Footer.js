import React from 'react';
import { Container, Segment, Grid, Header, List, Divider, Image } from 'semantic-ui-react';

function FooterColumn(props) {
    return (
        <Grid.Column width={props.width || 5}>
            {props.header ? <Header inverted as='h4'>{props.header}</Header> : null}
            <List link inverted>
                {props.children}
            </List>
        </Grid.Column>
    )
}

function AboutAppColumn() {
    return (
        <FooterColumn header={<><em>Quality-time</em> v{process.env.REACT_APP_VERSION}</>} >
            <List.Item as='a' href="https://www.ictu.nl/about-us">Developed by ICTU</List.Item>
            <List.Item as='a' href='https://github.com/ICTU/quality-time/blob/master/LICENSE'>License</List.Item>
            <List.Item as='a' href='https://quality-time.readthedocs.io/en/latest/changelog.html'>Changelog</List.Item>
            <List.Item as='a' href="">Source code</List.Item>
        </FooterColumn>
    )
}

function AboutReportColumn(props) {
    return (
        <FooterColumn width={6} header="About this report">
            <List.Item>{props.report.title}</List.Item>
            <List.Item>{props.report.subtitle || <span>&nbsp;</span>}</List.Item>
            <List.Item>{props.last_update.toLocaleDateString()}</List.Item>
            <List.Item>{props.last_update.toLocaleTimeString()}</List.Item>
        </FooterColumn>
    )
}

function QuoteColumn() {
    return (
        <FooterColumn width={6}>
            <List.Item><em>Quality without results is pointless.</em></List.Item>
            <List.Item><em>Results without quality is boring.</em></List.Item>
            <List.Item>Johan Cruyff</List.Item>
        </FooterColumn>
    )
}

function SupportColumn() {
    return (
        <FooterColumn header='Support'>
            <List.Item as='a' href="https://github.com/ICTU/quality-time/blob/master/README.md">Documentation</List.Item>
            <List.Item as='a' href="https://quality-time.readthedocs.io/en/latest/usage.html">User manual</List.Item>
            <List.Item as='a' href="https://github.com/ICTU/quality-time/issues">Known issues</List.Item>
            <List.Item as='a' href="https://github.com/ICTU/quality-time/issues/new">Report an issue</List.Item>
        </FooterColumn>
    )
}

export function Footer(props) {
    return (
        <Segment inverted style={{ margin: '5em 0em 0em', padding: '5em 0em 3em' }}>
            <Container>
                <Grid divided inverted stackable textAlign='center' verticalAlign='middle'>
                    <AboutAppColumn />
                    {props.report ? <AboutReportColumn {...props} /> : <QuoteColumn />}
                    <SupportColumn />
                </Grid>
                <Divider inverted section />
                <Image centered size='mini' src='./favicon.ico' />
            </Container>
        </Segment>
    )
}
