import React, { Component } from 'react';
import { Dropdown } from 'semantic-ui-react';

class SourceType extends Component {
  constructor(props) {
    super(props);
    this.state = { edited_source_type: this.props.source_type, edit: false, hover: false }
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
      this.setState({ edit: false, edited_source_type: this.props.source_type })
    }
  }
  onSubmit(event, { name, value }) {
    event.preventDefault();
    this.setState( {edit : false, edited_source_type: value })
    fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/metric/${this.props.metric_uuid}/source/${this.props.source_uuid}/type`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: value})
    })
  }
  render() {
    let options = [];
    let self = this;
    this.props.datamodel["metrics"][this.props.metric_type]["sources"].forEach(
      (key) => { options.push({ text: self.props.datamodel["sources"][key]["name"], value: key }) });
    if (this.state.edit) {
      return (
        <Dropdown fluid selectOnNavigation={false} defaultOpen value={this.state.edited_source_type}
          options={options} onChange={(e, { name, value }) => this.onSubmit(e, { name, value})} tabIndex="0" />
      )
    }
    const style = this.state.hover ? { borderBottom: "1px dotted #000000" } : { height: "1em" };
    return (
      <div onClick={(e) => this.onEdit(e)} onKeyPress={(e) => this.onEdit(e)}
        onMouseEnter={(e) => this.onMouseEnter(e)} onMouseLeave={(e) => this.onMouseLeave(e)} style={style} tabIndex="0">
        {this.props.datamodel["sources"][this.state.edited_source_type]["name"]}
      </div>
    )
  }
}

export { SourceType };
