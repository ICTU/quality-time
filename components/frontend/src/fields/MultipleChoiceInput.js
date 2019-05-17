import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceInput extends Component {
  constructor(props) {
    super(props);
    this.state = { value: props.value || [], options: this.options() }
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
    let options = new Set();
    this.props.options.forEach((option) => {options.add({key: option, text: option, value: option})});
    options = Array.from(options);
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
  }
  handleAddition = (event, { value }) => {
    event.preventDefault();
    this.setState({
      options: [{ key: value, text: value, value: value }, ...this.state.options],
    })
  }
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.value) {
      this.props.set_value(value);
    }
  }
  render() {
    let { required, set_value, allowAdditions, ...otherProps } = this.props;
    return (
      <Form>
        {this.props.readOnly ?
          <Form.Input
            {...otherProps}
          />
          :
          <Form.Dropdown
            {...otherProps}
            allowAdditions={allowAdditions}
            error={required && this.state.value.length === 0}
            fluid
            multiple
            onAddItem={this.handleAddition}
            onChange={(e, { value }) => this.onSubmit(e, value)}
            options={this.state.options}
            search
            selection
            value={this.state.value}
          />
        }
      </Form>
    )
  }
}

export { MultipleChoiceInput };
