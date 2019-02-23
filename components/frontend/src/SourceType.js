import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class SourceType extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_source_type: props.source_type };
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edited_source_type: this.props.source_type });
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    this.setState({ edited_source_type: value });
    const self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source_uuid}/type`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: value })
    }).then(
      () => self.props.reload()
    );
  }
  render() {
    let options = [];
    let self = this;
    this.props.datamodel.metrics[this.props.metric_type].sources.forEach(
      (key) => { options.push({ text: self.props.datamodel.sources[key].name, value: key }) });
    return (
      <Form>
        <Form.Dropdown label="Source type" search fluid selection selectOnNavigation={false}
          value={this.props.source_type}
          options={options} onChange={(e, { name, value }) => this.onSubmit(e, { name, value })} tabIndex="0" />
      </Form>
    )
  }
}

export { SourceType };
