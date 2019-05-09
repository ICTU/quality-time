import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from './fields/StringInput';

class ReportTitle extends Component {
    constructor(props) {
        super(props);
        this.state = { show_details: false }
    }
    onExpand(event) {
        event.preventDefault();
        this.setState((state) => ({ show_details: !state.show_details }));
    }
    set_report_attribute(key, value) {
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/${key}`, {
            method: 'post',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ [key]: value })
        }).then(
            () => self.props.reload()
        )
    }
    render() {
        return (
            <>
                <Header as='h1'
                        onClick={(e) => this.onExpand(e)}
                        onKeyPress={(e) => this.onExpand(e)}
                        tabIndex="0">
                    <Icon
                        name={this.state.show_details ? "caret down" : "caret right"}
                        size='large'
                    />
                    {this.props.report.title}
                </Header>
                {
                    this.state.show_details &&
                    <Segment>
                        <Grid stackable>
                            <Grid.Row columns={3}>
                                <Grid.Column>
                                    <StringInput
                                        label="Subject title"
                                        readOnly={this.props.readOnly}
                                        set_value={(value) => this.set_report_attribute("title", value)}
                                        value={this.props.report.title}
                                    />
                                </Grid.Column>
                            </Grid.Row>
                            {!this.props.readOnly &&
                                <Grid.Row>
                                    <Grid.Column>
                                        <Button
                                            basic
                                            floated='right'
                                            negative
                                            icon
                                            onClick={(e) => this.props.delete_report(e)}
                                            primary
                                        >
                                            <Icon name='trash' /> Delete report
                                        </Button>
                                    </Grid.Column>
                                </Grid.Row>
                            }
                        </Grid>
                    </Segment>
                }
            </>
        )
    }
}

export { ReportTitle };
