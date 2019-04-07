import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';
import { Input} from './Input';

class StringInputWithSuggestions extends Component {
  constructor(props) {
    super(props);
    this.state = { options: props.options, edited_value: props.value }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.value !== this.props.value) {
      this.setState({ edited_value: this.props.value });
    }
    if (prevProps.options !== this.props.options) {
      this.setState({ options: this.props.options });
    }
  }

  handleAddition = (e, { value }) => {
    this.setState({
      options: [{ text: value, value: value, key: value }, ...this.state.options],
    }, () => this.handleSubmit())
  }

  handleChange = (e, { value }) => {
    this.setState({ edited_value: value }, () => this.handleSubmit())
  }

  handleSubmit() {
    if (this.state.edited_value !== this.props.value) {
      this.props.set_value(this.state.edited_value);
    }
  }

  render() {
    let { set_value, ...otherProps } = this.props;
    return (
      <Form>
        <Form.Dropdown
          {...otherProps}
          allowAdditions
          clearable
          fluid
          onAddItem={this.handleAddition}
          onChange={this.handleChange}
          options={this.state.options}
          search
          selection
          value={this.state.edited_value}
        />
      </Form>
    )
  }
}

function StringInput(props) {
  const options = props.options || [];
  return props.readOnly || options.length === 0 ?
    <Input {...props} />
    :
    <StringInputWithSuggestions {...props} />
}

export { StringInput };
