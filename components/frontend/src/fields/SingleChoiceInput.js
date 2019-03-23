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
    const value_text = this.props.options.filter(({text, value}) => value === this.props.value)[0].text;
    return (
      <Form>
        {this.props.readOnly ?
          <Form.Input
            {...this.props}
            value={value_text}
          />
          :
          <Form.Dropdown
            {...this.props}
            fluid
            onChange={(e, { name, value }) => this.onSubmit(e, { name, value })}
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
