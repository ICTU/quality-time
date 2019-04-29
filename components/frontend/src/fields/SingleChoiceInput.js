import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class SingleChoiceInput extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_value: props.value };
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_value: this.props.value });
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    this.setState({ edited_value: value });
    if (value !== this.props.value) {
      this.props.set_value(value);
    }
  }
  render() {
    const value_text = this.props.options.filter(({ value }) => value === this.props.value)[0].text;
    let { set_value, options, ...otherProps } = this.props;
    options.sort((a, b) => a.text.localeCompare(b.text));
    return (
      <Form>
        {this.props.readOnly ?
          <Form.Input
            {...otherProps}
            value={value_text}
          />
          :
          <Form.Dropdown
            {...otherProps}
            fluid
            onChange={(e, { name, value }) => this.onSubmit(e, { name, value })}
            options={options}
            search
            selection
            selectOnNavigation={false}
            tabIndex="0"
            value={this.state.edited_value}
          />
        }
      </Form>
    )
  }
}

export { SingleChoiceInput };
