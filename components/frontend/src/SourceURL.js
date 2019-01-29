import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class SourceURL extends Component {
    constructor(props) {
      super(props);
      this.state = {edited_url: this.props.url, edit: false, hover: false}
    }
    onMouseEnter(event) {
      this.setState({ hover: true })
    }
    onMouseLeave(event) {
      this.setState({ hover: false })
    }
    onEdit() {
      this.setState({edit: true});
    }
    onChange(event) {
      this.setState({edited_url: event.target.value});
    }
    onKeyDown(event) {
      if (event.key === "Escape") {
        this.setState({edit: false, edited_url: this.props.url})
      }
    }
    onSubmit(event) {
      event.preventDefault();
      this.setState({edit: false});
      fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/metric/${this.props.metric_uuid}/source/${this.props.source_uuid}/url`, {
        method: 'post',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: this.state.edited_url})
      })
    }
    render() {
      if (this.state.edit) {
        return (
          <Form onSubmit={(e) => this.onSubmit(e)}>
            <Form.Input autoFocus focus fluid defaultValue={this.state.edited_url}
              onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
          </Form>
        )
      }
      const style = this.state.hover ? {borderBottom: "1px dotted #000000" } : {height: "1em"};
      return (
        <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
          {this.state.edited_url}
        </div>
      )
    }
  }

export { SourceURL };
