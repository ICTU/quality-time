import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from './fields/StringInput';
import { SingleChoiceInput} from './fields/SingleChoiceInput';

class SubjectTitle extends Component {
    constructor(props) {
        super(props);
        this.state = { show_details: false }
    }
    onExpand(event) {
        event.preventDefault();
        this.setState((state) => ({ show_details: !state.show_details }));
    }
    set_subject_attribute(key, value) {
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report_uuid}/subject/${this.props.subject_uuid}/${key}`, {
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
    delete_subject(event) {
        event.preventDefault();
        const self = this;
        fetch(`${window.server_url}/report/${this.props.report_uuid}/subject/${this.props.subject_uuid}`, {
            method: 'delete',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then(
            () => self.props.reload()
        );
    }
    render() {
        const subject_type = this.props.datamodel.subjects[this.props.subject.type] || { name: "Unknown subject type", description: "No description" };
        let options = [];
        Object.keys(this.props.datamodel.subjects).forEach(
            (key) => { options.push({ key: key, text: this.props.datamodel.subjects[key].name, value: key }) });
        return (
            <>
                <Header as='h2'>
                    <Icon
                        name={this.state.show_details ? "caret down" : "caret right"}
                        onClick={(e) => this.onExpand(e)}
                        onKeyPress={(e) => this.onExpand(e)}
                        size='large'
                        tabIndex="0"
                    />
                    {this.props.subject.name}
                </Header>
                {
                    this.state.show_details &&
                    <Segment basic>
                        <Header>
                            <Header.Content>
                                {subject_type.name}
                                <Header.Subheader>
                                    {subject_type.description}
                                </Header.Subheader>
                            </Header.Content>
                        </Header>
                        <Grid stackable>
                            <Grid.Row columns={3}>
                                <Grid.Column>
                                    <SingleChoiceInput
                                        label="Subject type"
                                        options={options}
                                        readOnly={this.props.readOnly}
                                        set_value={(value) => this.set_subject_attribute("type", value)}
                                        value={this.props.subject.type}
                                    />
                                </Grid.Column>
                                <Grid.Column>
                                    <StringInput
                                        label="Subject name"
                                        placeholder={subject_type.name}
                                        readOnly={this.props.readOnly}
                                        set_value={(value) => this.set_subject_attribute("name", value)}
                                        value={this.props.subject.name}
                                    />
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                        {!this.props.readOnly &&
                            <Button
                                basic
                                floated='right'
                                negative
                                icon
                                onClick={(e) => this.delete_subject(e)}
                                primary
                                style={{ marginBottom: "10px" }}
                            >
                                <Icon name='trash' /> Delete subject
                            </Button>
                        }
                    </Segment>
                }
            </>
        )
    }
}

export { SubjectTitle };
