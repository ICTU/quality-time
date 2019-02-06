import React, { Component } from 'react';
import { Button, Form, Grid, Header, Icon } from 'semantic-ui-react';


class SubjectTitleContainer extends Component {
    constructor(props) {
        super(props);
        this.state = { edited_title: this.props.subject.title, edit: false }
    }
    onEdit(event) {
        this.setState({ edit: true });
    }
    onChange(event) {
        this.setState({ edited_title: event.target.value });
    }
    onKeyDown(event) {
        if (event.key === "Escape") {
            this.setState({ edit: false, edited_title: this.props.subject.title })
        }
    }
    onSubmit(event) {
        event.preventDefault();
        this.setState({ edit: false });
        fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/title`, {
            method: 'post',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: this.state.edited_title })
        })
    }
    render() {
        return (
            <SubjectTitle title={this.state.edited_title} edit={this.state.edit}
                onSubmit={(e) => this.onSubmit(e)} onEdit={(e) => this.onEdit(e)}
                onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)}
                subject_uuid={this.props.subject_uuid} reload={this.props.reload} />)
    }
}

function SubjectTitle(props) {
    if (props.edit) {
        return (<SubjectTitleInput title={props.title} onSubmit={props.onSubmit} onChange={props.onChange}
            onKeyDown={props.onKeyDown} />)
    }
    return (
        <SubjectTitleDisplay title={props.title} onEdit={props.onEdit} onMouseEnter={props.onMouseEnter}
            onMouseLeave={props.onMouseLeave} subject_uuid={props.subject_uuid} reload={props.reload} />
    )
}

const SubjectTitleInput = props =>
    <Form onSubmit={(e) => props.onSubmit(e)}>
        <Form.Input autoFocus focus defaultValue={props.title}
            onChange={props.onChange} onKeyDown={props.onKeyDown} />
    </Form>


class SubjectTitleDisplay extends Component {
    constructor(props) {
        super(props);
        this.state = { editable: false }
    }
    onMouseEnter() {
        this.setState({ editable: true })
    }
    onMouseLeave() {
        this.setState({ editable: false })
    }
    delete_subject(event) {
        event.preventDefault();
        const self = this;
        fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}`, {
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
        const style = this.state.editable ? { borderBottom: "1px dotted #000000" } : {};
        return (
            <Grid>
                <Grid.Column key={0} width={15}>
                    <Header as='h2' onClick={this.props.onEdit} onKeyPress={this.props.onEdit} style={style}
                        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} tabIndex="0" >
                        {this.props.title}
                    </Header>
                </Grid.Column>
                <Grid.Column key={1} width={1}>
                    <Button icon primary negative basic
                        onClick={(e) => this.delete_subject(e)}>
                        <Icon name='trash alternate' />
                    </Button>
                </Grid.Column>
            </Grid>
        )
    }
}

export { SubjectTitleContainer };
