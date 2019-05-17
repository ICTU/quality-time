import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';
import { DateInput as CalendarDateInput } from 'semantic-ui-calendar-react';
import { Input } from './Input';

class EditableDateInput extends Component {
    constructor(props) {
        super(props);
        this.state = { edited_date: props.value }
    }
    onChange = (event, { name, value }) => {
        this.setState({ edited_date: value })
        this.props.set_value(value)
    }
    render() {
        return (
            <Form>
                <CalendarDateInput
                    dateFormat="YYYY-MM-DD"
                    disabled={this.props.readOnly}
                    label={this.props.label}
                    onChange={this.onChange}
                    error={this.props.required && this.state.edited_date === ""}
                    value={this.state.edited_date}
                />
            </Form>
        )
    }
}

function DateInput(props) {
    return props.readOnly ?
      <Input {...props} icon='calendar' />
      :
      <EditableDateInput {...props} />
  }

export { DateInput };