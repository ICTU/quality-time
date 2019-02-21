import React, { Component } from 'react';
import { Dropdown, Form } from 'semantic-ui-react';

class StringParameter extends Component {
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
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${this.props.parameter_key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [self.props.parameter_key]: self.state.edited_value })
    }).then(() => this.props.reload())
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

class MultipleChoiceParameter extends Component {
  onSubmit(event, value) {
    console.log(value);
    event.preventDefault();
    let self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${this.props.parameter_key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [self.props.parameter_key]: value })
    }).then(() => this.props.reload())
  }
  render() {
    const options = this.props.parameter_values.map((value) => ({ key: value, text: value, value: value }));
    return (
      <Dropdown
        defaultValue={this.props.parameter_value} onChange={(e, { value }) => this.onSubmit(e, value)}
        fluid multiple selection options={options} />
    )
  }
}

function SourceParameter(props) {
  return (
    props.parameter_type === "string" ?
      <StringParameter report_uuid={props.report_uuid} source_uuid={props.source_uuid}
        parameter_key={props.parameter_key} reload={props.reload}
        parameter_value={props.parameter_value} />
      :
      <MultipleChoiceParameter report_uuid={props.report_uuid} source_uuid={props.source_uuid}
        parameter_key={props.parameter_key} reload={props.reload}
        parameter_values={props.parameter_values}
        parameter_value={props.parameter_value} />
  )
}

export { SourceParameter };
