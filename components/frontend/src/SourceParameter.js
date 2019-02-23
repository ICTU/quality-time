import React, { Component } from 'react';
import { Dropdown, Form } from 'semantic-ui-react';

class StringParameter extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: this.props.parameter_value }
  }
  onChange(event) {
    this.setState({ edited_value: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_value: this.props.parameter_value })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    let self = this;
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
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Input focus fluid defaultValue={this.state.edited_value}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
      </Form>
    )
  }
}

class MultipleChoiceParameter extends Component {
  onSubmit(event, value) {
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
