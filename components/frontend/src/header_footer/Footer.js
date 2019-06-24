import React from 'react';
import { Container, Segment, Grid, Header, List, Divider, Image } from 'semantic-ui-react';

export function Footer(props) {
    return (
        <Segment inverted style={{ margin: '5em 0em 0em', padding: '5em 0em 3em' }}>
            <Container>
                <Grid divided inverted stackable textAlign='center' verticalAlign='middle'>
                    <Grid.Column width={5}>
                        <Header inverted as='h4'>About <em>Quality-time</em></Header>
                        <List link inverted>
                            <List.Item as='a' href="https://www.ictu.nl/about-us">Developed by ICTU</List.Item>
                            <List.Item as='a' href='https://github.com/ICTU/quality-time/blob/master/LICENSE'>License</List.Item>
                            <List.Item as='a' href='https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md'>Changelog</List.Item>
                            <List.Item as='a' href="https://github.com/ICTU/quality-time">Source code</List.Item>
                        </List>
                    </Grid.Column>
                    <Grid.Column width={6}>
                        {props.report ?
                            <>
                                <Header inverted as='h4' content="About this report" />
                                <List inverted>
                                    <List.Header>{props.report.title}</List.Header>
                                    <List.Item>{props.report.subtitle}</List.Item>
                                    <List.Item>{props.last_update.toLocaleString()} <span role="img" aria-label="little yellow diamond shaped separator">🔸</span> <em>Quality-time</em> v{process.env.REACT_APP_VERSION}</List.Item>
                                </List>
                            </>
                            :
                            <List inverted>
                                <List.Item><em>Quality without results is pointless.</em></List.Item>
                                <List.Item><em>Results without quality is boring.</em></List.Item>
                                <List.Item>Johan Cruyff</List.Item>
                            </List>
                        }
                    </Grid.Column>
                    <Grid.Column width={5}>
                        <Header inverted as='h4' content='Support' />
                        <List link inverted>
                            <List.Item as='a' href="https://github.com/ICTU/quality-time/blob/master/README.md">Documentation</List.Item>
                            <List.Item as='a' href="https://github.com/ICTU/quality-time/blob/master/USAGE.md">User manual</List.Item>
                            <List.Item as='a' href="https://github.com/ICTU/quality-time/issues">Known issues</List.Item>
                            <List.Item as='a' href="https://github.com/ICTU/quality-time/issues/new">Report an issue</List.Item>
                        </List>
                    </Grid.Column>
                </Grid>
                <Divider inverted section />
                <Image centered size='mini' src='./favicon.ico' />
            </Container>
        </Segment>
    )
}
