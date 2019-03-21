import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceParameterAddition extends Component {
  constructor(props) {
    super(props);
    this.state = { value: props.parameter_value, options: this.options() }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.parameter_values !== this.props.parameter_values) {
      this.setState({ options: this.options() })
    }
  }
  options() {
    return this.props.parameter_values.map((value) => ({ key: value, text: value, value: value }));
  }
  handleAddition = (e, { value }) => {
    this.setState({
      options: [{ text: value, value }, ...this.state.options],
    })
  }
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.value) {
      this.props.set_parameter(this.props.parameter_key, value);
    }
  }
  render() {
    return (
      <Form >
        {this.props.readOnly ?
          <Form.Input label={this.props.label} value={this.state.value} readOnly />
          :
          <Form.Dropdown 
            allowAdditions
            fluid  
            label={this.props.label}
            multiple
            onAddItem={this.handleAddition}
            onChange={(e, { value }) => this.onSubmit(e, value)}
            options={this.state.options} 
            selection
            search 
            value={this.state.value || []} 
          />
        }
      </Form>
    )
  }
}

export { MultipleChoiceParameterAddition };
