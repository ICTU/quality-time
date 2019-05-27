import React, { Component } from 'react';
import { Form, Label } from 'semantic-ui-react';

class IntegerInput extends Component {
    constructor(props) {
        super(props);
        this.state = { edited_value: this.props.value || 0 }
    }
    componentDidUpdate(prevProps) {
        if (prevProps.value !== this.props.value) {
            this.setState({ edited_value: this.props.value || 0 })
        }
    }
    onChange(event) {
        this.setState({ edited_value: event.target.value || 0 });
    }
    onKeyDown(event) {
        if (event.key === "Escape") {
            this.setState({ edited_value: this.props.value || 0 })
        }
    }
    onSubmit(event) {
        event.preventDefault();
        if (this.state.edited_value !== this.props.value) {
            this.props.set_value(parseInt(this.state.edited_value, 10) || 0);
        }
    }
    render() {
        let { prefix, set_value, unit, ...props } = this.props;
        return (
            <Form onSubmit={(e) => this.onSubmit(e)}>
                <Form.Group style={{ marginBottom: '0px' }}>
                    <Form.Input
                        {...props}
                        fluid
                        focus
                        labelPosition="right"
                        min="0"
                        onBlur={(e) => this.onSubmit(e)}
                        onChange={(e) => this.onChange(e)}
                        onKeyDown={(e) => this.onKeyDown(e)}
                        onSubmit={(e) => this.onSubmit(e)}
                        type="number"
                        value={this.state.edited_value}
                        width={16}
                    >
                        {prefix ? <Label basic>{prefix}</Label> : null}
                        <input />
                        <Label basic>{unit}</Label>
                    </Form.Input>
                </Form.Group>
            </Form>
        )
    }
}

export { IntegerInput };