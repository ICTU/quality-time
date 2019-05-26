import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from './fields/StringInput';
import { SubjectType } from './SubjectType';

class SubjectTitle extends Component {
    constructor(props) {
        super(props);
        this.state = { show_details: false }
    }
    onExpand(event) {
        event.preventDefault();
        this.setState((state) => ({ show_details: !state.show_details }));
    }
    render() {
        const current_subject_type = this.props.datamodel.subjects[this.props.subject.type] || { name: "Unknown subject type", description: "No description" };
        return (
            <>
                <Header as='h2' style={{marginTop: 50}}
                    onClick={(e) => this.onExpand(e)}
                    onKeyPress={(e) => this.onExpand(e)}
                    tabIndex="0">
                    <Icon
                        name={this.state.show_details ? "caret down" : "caret right"}
                        size='large'
                    />
                    {this.props.subject.name}
                </Header>
                {
                    this.state.show_details &&
                    <Segment>
                        <Header>
                            <Header.Content>
                                {current_subject_type.name}
                                <Header.Subheader>
                                    {current_subject_type.description}
                                </Header.Subheader>
                            </Header.Content>
                        </Header>
                        <Grid stackable>
                            <Grid.Row columns={3}>
                                <Grid.Column>
                                    <SubjectType
                                        datamodel={this.props.datamodel}
                                        readOnly={this.props.readOnly}
                                        set_value={(value) => this.props.set_subject_attribute("type", value)}
                                        subject_type={this.props.subject.type}
                                    />
                                </Grid.Column>
                                <Grid.Column>
                                    <StringInput
                                        label="Subject name"
                                        placeholder={current_subject_type.name}
                                        readOnly={this.props.readOnly}
                                        set_value={(value) => this.props.set_subject_attribute("name", value)}
                                        value={this.props.subject.name}
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
                                            onClick={(e) => this.props.delete_subject(e)}
                                            primary
                                        >
                                            <Icon name='trash' /> Delete subject
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

export { SubjectTitle };
