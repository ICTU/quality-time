import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class ReportTitleContainer extends Component {
    constructor(props) {
        super(props);
        this.state = { title: props.report ? props.report.title : "Quality-time", edit: false }
    }
    onEdit(event) {
        this.setState((state) => ({ edit: true, previous_title: state.title }));
    }
    onChange(event) {
        this.setState({ title: event.target.value });
    }
    onKeyDown(event) {
        if (event.key === "Escape") {
            this.setState((state) => ({ edit: false, title: state.previous_title }))
        }
    }
    onSubmit(event) {
        event.preventDefault();
        this.setState({ edit: false });
        let self = this;
        fetch(`${window.server_url}/report/${this.props.report.report_uuid}/title`, {
            method: 'post',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: this.state.title })
        }).then(() => self.props.reload())
    }
    render() {
        return (
            <ReportTitle title={this.state.title} edit={this.state.edit}
                user={this.props.user}
                onSubmit={(e) => this.onSubmit(e)} onEdit={(e) => this.onEdit(e)}
                onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />)
    }
}

function ReportTitle(props) {
    if (props.edit) {
        return (<ReportTitleInput title={props.title} onSubmit={props.onSubmit} onChange={props.onChange}
            onKeyDown={props.onKeyDown} />)
    }
    return (
        <ReportTitleDisplay title={props.title} onEdit={props.onEdit} onMouseEnter={props.onMouseEnter}
            onMouseLeave={props.onMouseLeave} user={props.user} />
    )
}

const ReportTitleInput = props =>
    <Form onSubmit={(e) => props.onSubmit(e)}>
        <Form.Input autoFocus focus defaultValue={props.title} readOnly={(props.user === null)}
            onChange={props.onChange} onKeyDown={props.onKeyDown} />
    </Form>


class ReportTitleDisplay extends Component {
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
    render() {
        if (this.props.user === null) { return (<font size="+3">{this.props.title}</font>) }
        const style = this.state.editable ? { borderBottom: "1px dotted #FFFFFF" } : {};
        return (
            <div onClick={this.props.onEdit} onKeyPress={this.props.onEdit} onMouseEnter={(e) => this.onMouseEnter(e)}
                onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
                <font size="+3">
                    {this.props.title}
                </font>
            </div>
        )
    }
}


export { ReportTitleContainer };
