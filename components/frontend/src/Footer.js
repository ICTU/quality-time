import React, { Component } from 'react';
import { Container, Segment, Grid, Header, List, Divider, Image } from 'semantic-ui-react';

class Footer extends Component {

    render() {
        return (
            <Segment inverted vertical style={{ margin: '5em 0em 0em', padding: '5em 0em' }}>
                <Container textAlign='center'>
                    <Grid divided inverted stackable>
                        <Grid.Column width={3}>
                            <Header inverted as='h4' content='Group 1' />
                            <List link inverted>
                                <List.Item as='a'>Link One</List.Item>
                                <List.Item as='a'>Link Two</List.Item>
                                <List.Item as='a'>Link Three</List.Item>
                                <List.Item as='a'>Link Four</List.Item>
                            </List>
                        </Grid.Column>
                        <Grid.Column width={3}>
                            <Header inverted as='h4' content='Group 2' />
                            <List link inverted>
                                <List.Item as='a'>Link One</List.Item>
                                <List.Item as='a'>Link Two</List.Item>
                                <List.Item as='a'>Link Three</List.Item>
                                <List.Item as='a'>Link Four</List.Item>
                            </List>
                        </Grid.Column>
                        <Grid.Column width={3}>
                            <Header inverted as='h4' content='Group 3' />
                            <List link inverted>
                                <List.Item as='a'>Link One</List.Item>
                                <List.Item as='a'>Link Two</List.Item>
                                <List.Item as='a'>Link Three</List.Item>
                                <List.Item as='a'>Link Four</List.Item>
                            </List>
                        </Grid.Column>
                        <Grid.Column width={7}>
                            <Header inverted as='h4' content='Footer Header' />
                            <p>
                                Extra space for a call to action inside the footer that could help re-engage users.
            </p>
                        </Grid.Column>
                    </Grid>

                    <Divider inverted section />
                    <Image centered size='mini' src='./favicon.ico' />
                    <List horizontal inverted divided link size='small'>
                        <List.Item as='a' href='#'>
                            Site Map
                    </List.Item>
                        <List.Item as='a' href='#'>
                            Contact Us
                    </List.Item>
                        <List.Item as='a' href='#'>
                            Terms and Conditions
                    </List.Item>
                        <List.Item as='a' href='#'>
                            Privacy Policy
                    </List.Item>
                    </List>
                </Container>
            </Segment>
        )
    }
}


export { Footer };