import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class StringParameterWithSuggestions extends Component {
  constructor(props) {
    super(props);
    this.state = { options: props.options, edited_value: props.parameter_value }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.parameter_value !== this.props.parameter_value) {
      this.setState({ edited_value: this.props.parameter_value })
    }
  }

  handleAddition = (e, { value }) => {
    console.log("handleAddition", value);
    this.setState({
      options: [{ text: value, value: value, key: value }, ...this.state.options],
    }, () => this.handleSubmit())
  }

  handleChange = (e, { value }) => {
    console.log("handleChange", e, value)
    this.setState({ edited_value: value }, () => this.handleSubmit())
  }

  handleSubmit() {
    console.log("handleSubmit", this.state.edited_value);
    if (this.state.edited_value !== this.props.parameter_value) {
      console.log("handleSubmit, calling set_parameter", this.props.parameter_key, this.state.edited_value);
      this.props.set_parameter(this.props.parameter_key, this.state.edited_value);
    }
  }

  render() {
    return (
      <Form>
        <Form.Dropdown
          allowAdditions
          fluid
          label={this.props.parameter_name}
          onAddItem={this.handleAddition}
          onChange={this.handleChange}
          options={this.state.options}
          placeholder={this.props.placeholder}
          search
          selection
          value={this.state.edited_value}
        />
      </Form>
    )
  }
}

class StringParameterWithoutSuggestions extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: this.props.parameter_value }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.parameter_value !== this.props.parameter_value) {
      this.setState({ edited_value: this.props.parameter_value })
    }
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
      <Form>
        <Form.Input
          fluid
          focus
          label={this.props.parameter_name}
          onBlur={(e) => this.onSubmit(e)}
          onChange={(e) => this.onChange(e)}
          onKeyDown={(e) => this.onKeyDown(e)}
          onSubmit={(e) => this.onSubmit(e)}
          placeholder={this.props.placeholder}
          readOnly={this.props.readOnly}
          value={this.state.edited_value || ""}
        />
      </Form>
    )
  }
}

function StringParameter(props) {
  const options = props.options || [];
  return props.readOnly || options.length === 0 ?
    <StringParameterWithoutSuggestions {...props} />
    :
    <StringParameterWithSuggestions {...props} />
}

export { StringParameter };
