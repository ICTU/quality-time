import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class Comment extends Component {
  constructor(props) {
    super(props);
    this.state = {edited_comment: this.props.comment, edit: false, hover: false}
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
    this.setState({edited_comment: event.target.value});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({edit: false, edited_comment: this.props.comment})
    }
  }
  onSubmit(event) {
    event.preventDefault();
    const self = this;
    this.setState({edit: false});
    fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/metric/${this.props.metric_uuid}/comment`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({comment: this.state.edited_comment})
    }).then(
      () => self.props.reload()
    )
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
    const style = this.state.hover ? {overflow: "hidden", borderBottom: "1px dotted #000000" } : {overflow: "hidden"};
    return (
      <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
      onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
        {this.state.edited_comment}
      </div>
    )
  }
}

export { Comment };
