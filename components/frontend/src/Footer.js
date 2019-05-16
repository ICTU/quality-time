import React, { Component } from 'react';
import { Container, Segment, Grid, Header, List, Divider, Image } from 'semantic-ui-react';

class Footer extends Component {

    render() {
        return (
            <Segment inverted vertical style={{ margin: '5em 0em 0em', padding: '5em 0em 3em' }}>
                <Container textAlign='center'>
                    <Grid divided inverted stackable>
                    <Grid.Column width={4}>
                            <Header inverted as='h4' content='Quality-time' />
                            <List horizontal inverted link size='small'>
                                <List.Item > <Image centered size='mini' src='./favicon.ico' /> </List.Item>
                                <List.Item as='a' href="https://www.ictu.nl/about-us"> Developed and maintained by ICTU. </List.Item>
                                <List.Item as='a' href='https://github.com/ICTU/quality-time/blob/master/LICENSE'>
                                    Terms and Conditions
                                </List.Item>
                            </List>

                        </Grid.Column>
                        <Grid.Column width={4}>
                            <Header inverted as='h4' content='Support' />
                            <List link inverted>
                                <List.Item as='a' href="https://github.com/ICTU/quality-time">Github</List.Item>
                                <List.Item as='a' href="https://github.com/ICTU/quality-time/blob/master/README.md">Readme</List.Item>
                                <List.Item as='a' href="https://github.com/ICTU/quality-time/issues">Known issues</List.Item>
                                <List.Item as='a' href="https://github.com/ICTU/quality-time/issues/new">Report an issue</List.Item>
                            </List>
                        </Grid.Column>
                        <Grid.Column width={7}>
                            <Header inverted as='h4' content={this.props.report ? this.props.report.title : "Quality-time"} />
                            <List link inverted>
                                <List.Item>{this.props.report ? this.props.report.subtitle : ""}</List.Item>
                                <br></br>
                                <List.Item>Creation date of report: {this.props.last_update.toLocaleString()}</List.Item>
                                <List.Item>Quality-time version: 0.1</List.Item>
                            </List>
                        </Grid.Column>
                    </Grid>
                    <Divider inverted section />
                </Container>
            </Segment>
        )
    }
}


export { Footer };