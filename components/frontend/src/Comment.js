import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class Comment extends Component {
  constructor(props) {
    super(props);
    this.state = {edited_comment: this.props.comment, edit: false}
  }
  onEdit() {
    this.setState({edit: true});
  }
  onChange(event) {
    this.setState({edited_comment: event.target.value});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({edit: false, edited_comment: this.props.comment})
    }
  }
  onSubmit(event) {
    event.preventDefault();
    this.setState({edit: false});
    fetch(`http://localhost:8080/comment/${this.props.metric_id}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({comment: this.state.edited_comment})
    })
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          <Form.Input autoFocus focus fluid defaultValue={this.state.edited_comment}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
        </Form>
      )
    }
    const style = this.props.editable ? {outline: 1, outlineStyle: "dotted", minHeight: "1em"} : {};
    return (
      <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)} style={style} tabIndex="0">
        {this.state.edited_comment}
      </div>
    )
  }
}

export { Comment };
