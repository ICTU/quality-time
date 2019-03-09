import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

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
    fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${this.props.parameter_key}`, {
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
        <Form.Input label={this.props.parameter_name} focus fluid defaultValue={this.state.edited_value}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)}
          onBlur={(e) => this.onSubmit(e)} readOnly={(this.props.user === null)} />
      </Form>
    )
  }
}

class MultipleChoiceParameter extends Component {
  onSubmit(event, value) {
    event.preventDefault();
    let self = this;
    fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${this.props.parameter_key}`, {
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
      <Form >
        {this.props.user === null ?
        <Form.Input label={this.props.parameter_name} value={this.props.parameter_value} readOnly />
        :
        <Form.Dropdown label={this.props.parameter_name}
          defaultValue={this.props.parameter_value} onChange={(e, { value }) => this.onSubmit(e, value)}
          fluid multiple selection options={options} />
        }
      </Form>
    )
  }
}

function SourceParameter(props) {
  return (
    props.parameter_type === "string" ?
      <StringParameter report_uuid={props.report_uuid} source_uuid={props.source_uuid}
        parameter_key={props.parameter_key} reload={props.reload} user={props.user}
        parameter_value={props.parameter_value} parameter_name={props.parameter_name} />
      :
      <MultipleChoiceParameter report_uuid={props.report_uuid} source_uuid={props.source_uuid}
        parameter_key={props.parameter_key} reload={props.reload} user={props.user}
        parameter_values={props.parameter_values} parameter_name={props.parameter_name}
        parameter_value={props.parameter_value} />
  )
}

export { SourceParameter };
