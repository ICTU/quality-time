import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class SourceParameter extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: this.props.parameter_value, edit: false, hover: false }
  }
  onMouseEnter(event) {
    this.setState({ hover: true })
  }
  onMouseLeave(event) {
    this.setState({ hover: false })
  }
  onEdit() {
    this.setState({ edit: true });
  }
  onChange(event) {
    this.setState({ edited_value: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edit: false, edited_value: this.props.parameter_value })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    let self = this;
    this.setState({ edit: false });
    fetch(`http://localhost:8080/report/source/${this.props.source_uuid}/parameter/${this.props.parameter_key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [self.props.parameter_key]: self.state.edited_value })
    })
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          <Form.Input autoFocus focus fluid defaultValue={this.state.edited_value}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
        </Form>
      )
    }
    const style = this.state.hover ? { overflow: "hidden", borderBottom: "1px dotted #000000" } : { overflow: "hidden" };
    return (
      <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)}
        style={style} tabIndex="0">
        {this.state.edited_value || "Enter parameter value"}
      </div>
    )
  }
}

export { SourceParameter };
