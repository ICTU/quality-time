import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';


class SourceName extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_name: props.name, edit: false, hover: false }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.name !== this.props.name) {
      this.setState({ edited_name: this.props.name })
    }
  }
  onMouseEnter(event) {
    this.setState({ hover: true })
  }
  onMouseLeave(event) {
    this.setState({ hover: false })
  }
  onEdit() {
    this.setState({ edit: true });
  }
  onChange(event) {
    this.setState({ edited_name: event.target.value });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edit: false, edited_name: this.props.name })
    }
  }
  onSubmit(event) {
    event.preventDefault();
    const self = this;
    this.setState({ edit: false });
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}/name`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: this.state.edited_name })
    }).then(
      () => self.props.reload()
    )
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          <Form.Input autoFocus focus fluid defaultValue={this.state.edited_name}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
        </Form>
      )
    }
    const style = this.state.hover ? { overflow: "hidden", borderBottom: "1px dotted #000000" } : { overflow: "hidden" };
    return (
      <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
        {this.state.edited_name}
      </div>
    )
  }
}

export { SourceName };
