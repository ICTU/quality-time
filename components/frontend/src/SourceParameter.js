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
    if (this.state.edited_value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, this.state.edited_value);
    }
  }
  render() {
    return (
      <Form onSubmit={(e) => this.onSubmit(e)}>
        <Form.Input label={this.props.parameter_name} focus fluid defaultValue={this.state.edited_value}
          onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)}
          onBlur={(e) => this.onSubmit(e)} readOnly={this.props.readOnly} />
      </Form>
    )
  }
}

class MultipleChoiceParameter extends Component {
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.parameter_value) {
      this.props.set_parameter(this.props.parameter_key, value);
    }
  }
  render() {
    const options = this.props.parameter_values.map((value) => ({ key: value, text: value, value: value }));
    return (
      <Form >
        {this.props.readOnly ?
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

class SourceParameter extends Component {
  set_source_parameter(key, value) {
    fetch(`${window.server_url}/report/${this.props.report_uuid}/source/${this.props.source_uuid}/parameter/${key}`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ [key]: value })
    }).then(() => this.props.reload())
  }
  render() {
    const readOnly = this.props.user === null;
    return (
      this.props.parameter_type === "string" ?
        <StringParameter set_parameter={(k,v ) => this.set_source_parameter(k, v)}
          parameter_key={this.props.parameter_key} readOnly={readOnly}
          parameter_value={this.props.parameter_value} parameter_name={this.props.parameter_name} />
        :
        <MultipleChoiceParameter set_parameter={(k, v) => this.set_source_parameter(k, v)}
          parameter_key={this.props.parameter_key} readOnly={readOnly}
          parameter_values={this.props.parameter_values} parameter_name={this.props.parameter_name}
          parameter_value={this.props.parameter_value} />
    )
  }
}

export { SourceParameter };
