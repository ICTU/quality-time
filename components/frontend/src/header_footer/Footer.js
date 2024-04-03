import { Container, Divider, Grid, Header, Icon, Image, List, Segment } from 'semantic-ui-react';
import { childrenPropType, datePropType, reportPropType } from '../sharedPropTypes';
import { number, object, oneOfType, string } from 'prop-types';
import './Footer.css';

function FooterItem({ children, icon, url }) {
    const item = icon ? <><Icon name={icon} /> {children}</> : children;
    return url ? <List.Item as="a" href={url}>{item}</List.Item> : <List.Item>{item}</List.Item>;
}
FooterItem.propTypes = {
    children: childrenPropType,
    icon: string,
    url: string,
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
FooterColumn.propTypes = {
    children: childrenPropType,
    header: oneOfType([object, string]),
    textAlign: string,
    width: number,
}

function FooterCenterColumn({ header, children }) {
    return (
        <FooterColumn header={header} width={8} textAlign="center">
            {children}
        </FooterColumn>
    )
}
FooterCenterColumn.propTypes = {
    header: oneOfType([object, string]),
    children: childrenPropType,
}

function FooterSideColumn({ header, children }) {
    return (
        <FooterColumn header={header} width={3} textAlign="left">
            {children}
        </FooterColumn>
    )
}
FooterSideColumn.propTypes = {
    header: oneOfType([object, string]),
    children: childrenPropType,
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
    last_update = last_update ?? new Date();
    // When exporting to PDF, window.location.href may not be the correct URL. This is fixed by having the user's
    // browser pass the correct URL as search parameter and use that instead:
    const reportURL = new URLSearchParams(window.location.search).get("report_url") ?? window.location.href;
    return (
        <FooterCenterColumn header="About this report">
            <FooterItem url={reportURL}>{report.title}</FooterItem>
            <FooterItem>{report.subtitle}</FooterItem>
            <FooterItem>{last_update.toLocaleDateString()}</FooterItem>
            <FooterItem>{last_update.toLocaleTimeString()}</FooterItem>
        </FooterCenterColumn>
    )
}
AboutReportColumn.propTypes = {
    report: reportPropType,
    last_update: datePropType,
}

function QuoteColumn() {
    const quotes = [
        ["If it hurts, do it more frequently,", "and bring the pain forward.", "Jez Humble"],
        ["Quality without results is pointless.", "Results without quality is boring.", "Johan Cruyff"],
        ["Quality is free,", "but only to those who are willing to pay heavily for it.", "DeMarco and Lister"],
        ["Quality means doing it right", "even when no one is looking.", "Henry Ford"],
        ["Quality... you know what it is,", "yet you don't know what it is.", "Robert M. Pirsig"]
    ]
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    return (
        <FooterCenterColumn>
            <FooterItem><em>{randomQuote[0]}</em></FooterItem>
            <FooterItem><em>{randomQuote[1]}</em></FooterItem>
            <FooterItem>{randomQuote[2]}</FooterItem>
        </FooterCenterColumn>
    )
}

export function Footer({ report, last_update }) {
    return (
        <Segment inverted id="Footer" style={{ margin: '5em 0em 0em', padding: '5em 0em 3em', backgroundColor: "#1b1c1d" }}>
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
Footer.propTypes = {
    report: reportPropType,
    last_update: datePropType,
}
