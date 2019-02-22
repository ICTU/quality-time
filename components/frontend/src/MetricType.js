import React, { Component } from 'react';
import { Dropdown } from 'semantic-ui-react';

class MetricType extends Component {
  constructor(props) {
    super(props);
    this.state = { edit: false, hover: false, edited_metric_type: props.metric_type };
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
  onClose() {
    this.setState({ edit: false });
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState({ edit: false, edited_metric_type: this.props.metric_type });
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    let self = this;
    this.setState({ edit: false, edited_metric_type: value });
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/type`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: value })
    }).then(() => self.props.reload());
  }
  render() {
    let options = [];
    let self = this;
    Object.keys(this.props.datamodel["metrics"]).forEach(
      (key) => { options.push({ text: self.props.datamodel["metrics"][key]["name"], value: key }) });
    if (this.state.edit) {
      return (
        <Dropdown fluid selectOnNavigation={false} defaultOpen value={this.state.edited_metric_type}
          options={options} onChange={(e, { name, value }) => this.onSubmit(e, { name, value })} tabIndex="0" />
      )
    }
    const style = this.state.hover ? { borderBottom: "1px dotted #000000" } : { height: "1em" };
    return (
      <span onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
        {this.props.datamodel["metrics"][this.state.edited_metric_type]["name"]}
      </span>
    )
  }
}

export { MetricType };
