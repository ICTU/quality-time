import React, { Component } from 'react';
import { Form, Icon } from 'semantic-ui-react';


class Target extends Component {
  constructor(props) {
    super(props);
    this.state = {edited_target: this.props.target, edit: false}
  }
  onClick() {
    this.setState({edit: true});
  }
  onChange(event) {
    this.setState({edited_target: event.target.value});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({edit: false, edited_target: this.props.target})
    }
  }
  onSubmit(event) {
    event.preventDefault();
    this.setState({edit: false});
    fetch(`http://localhost:8080/target/${this.props.metric_id}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({target: this.state.edited_target})
    })
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          {this.props.direction}
          <Form.Input autoFocus focus fluid type="number" min="0" defaultValue={this.state.edited_target}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
          {this.props.unit}
        </Form>
      )
    }
    const style = this.state.edited_target ? {marginRight: "10px"} : {marginRight: "0px"};
    return (
      <div onClick={(e) => this.onClick(e)}>
        <span style={style}>
          {this.props.direction} {this.state.edited_target} {this.props.unit}
        </span>
        <Icon color='grey' name='edit' />
      </div>
    )
  }
}

export { Target };
