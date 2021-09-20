import React from 'react';
import { Container, Divider, Grid, Header, Icon, Image, List, Segment } from 'semantic-ui-react';

function FooterColumn({ children, header, textAlign, width }) {
    return (
        <Grid.Column width={width || 3} textAlign={textAlign || "left"}>
            {header ? <Header inverted as='h4'>{header}</Header> : null}
            <List link inverted>
                {children}
            </List>
        </Grid.Column>
    )
}

function AboutAppColumn() {
    return (
        <>
            <Grid.Column width={1} />
            <FooterColumn header={<><em>Quality-time</em> v{process.env.REACT_APP_VERSION}</>} >
                <List.Item as='a' href="https://www.ictu.nl/about-us"><Icon name="flask"/> Developed by ICTU</List.Item>
                <List.Item as='a' href='https://github.com/ICTU/quality-time/blob/master/LICENSE'><Icon name="copyright outline" /> License</List.Item>
                <List.Item as='a' href={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/changelog.html`}><Icon name="history" /> Changelog</List.Item>
                <List.Item as='a' href="https://github.com/ICTU/quality-time"><Icon name="code" /> Source code</List.Item>
            </FooterColumn>
        </>
    )
}

function AboutReportColumn({ report, last_update }) {
    return (
        <FooterColumn width={8} textAlign="center" header="About this report">
            <List.Item>{report.title}</List.Item>
            <List.Item>{report.subtitle || <span>&nbsp;</span>}</List.Item>
            <List.Item>{last_update.toLocaleDateString()}</List.Item>
            <List.Item>{last_update.toLocaleTimeString()}</List.Item>
        </FooterColumn>
    )
}

function QuoteColumn() {
    /* Use the zero-width non-joiner character to make this column the same height as the other two columns 
       so that the two dividers between the three columns are equal height as well
    */
    return (
        <FooterColumn textAlign='center' width={8} header="&zwnj;">
            <List.Item><em>Quality without results is pointless.</em></List.Item>
            <List.Item><em>Results without quality is boring.</em></List.Item>
            <List.Item>Johan Cruyff</List.Item>
            <List.Item>&zwnj;</List.Item>
        </FooterColumn>
    )
}

function SupportColumn() {
    return (
        <>
            <Grid.Column width={1} />
            <FooterColumn header='Support'>
                <List.Item as='a' href={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/`}><Icon name="book" /> Documentation</List.Item>
                <List.Item as='a' href={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/usage.html`}><Icon name="user outline" /> User manual</List.Item>
                <List.Item as='a' href="https://github.com/ICTU/quality-time/issues"><Icon name="bug" /> Known issues</List.Item>
                <List.Item as='a' href="https://github.com/ICTU/quality-time/issues/new"><Icon name="comment" /> Report an issue</List.Item>
            </FooterColumn>
        </>
    )
}

export function Footer({ report, last_update }) {
    return (
        <Segment inverted style={{ margin: '5em 0em 0em', padding: '5em 0em 3em' }}>
            <Container>
                <Grid inverted stackable verticalAlign='middle' columns={16}>
                    <Grid.Row>
                        <AboutAppColumn />
                        {report ? <AboutReportColumn report={report} last_update={last_update} /> : <QuoteColumn />}
                        <SupportColumn />
                    </Grid.Row>
                </Grid>
                <Divider inverted section />
                <Image centered size='mini' src='./favicon.ico' />
            </Container>
        </Segment>
    )
}
