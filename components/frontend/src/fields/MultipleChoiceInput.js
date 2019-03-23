import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceInput extends Component {
  constructor(props) {
    super(props);
    this.state = { value: props.value, options: this.options() }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.values !== this.props.values) {
      this.setState({ options: this.options() })
    }
    if (prevProps.value !== this.props.value) {
      this.setState({ value: this.props.value })
    }
  }
  options() {
    return this.props.options.map((value) => ({ key: value, text: value, value: value }));
  }
  handleAddition = (event, { value }) => {
    event.preventDefault();
    this.setState({
      options: [{ text: value, value }, ...this.state.options],
    })
  }
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.value) {
      this.props.set_value(value);
    }
  }
  render() {
    return (
      <Form >
        {this.props.readOnly ?
          <Form.Input
            {...this.props}
          />
          :
          <Form.Dropdown
            {...this.props}
            fluid
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

export { MultipleChoiceInput };
