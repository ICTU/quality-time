import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Subject } from './Subject.js';


class Subjects extends Component {
  onAddSubject(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report_uuid}/subject/new`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(
      () => self.props.reload()
    );
  }
  render() {
    return (
      <>
        {Object.keys(this.props.subjects).map((subject_uuid) =>
          <Subject key={subject_uuid} report_uuid={this.props.report_uuid} subject_uuid={subject_uuid}
            subject={this.props.subjects[subject_uuid]}
            search_string={this.props.search_string} datamodel={this.props.datamodel} reload={this.props.reload}
            report_date={this.props.report_date} nr_new_measurements={this.props.nr_new_measurements}
            readOnly={this.props.readOnly} />)}
        {!this.props.readOnly &&
          <Segment basic>
            <Button icon primary basic onClick={(e) => this.onAddSubject(e)}>
              <Icon name='plus' /> Add subject
            </Button>
          </Segment>}
      </>
    )
  }
}

export { Subjects };
