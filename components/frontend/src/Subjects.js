import React, { Component } from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Subject } from './Subject.js';


class Subjects extends Component {
  onAddSubject(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/subject/new`, {
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
        {Object.keys(this.props.report.subjects).map((subject_uuid) =>
          <Subject
            datamodel={this.props.datamodel}
            key={subject_uuid}
            nr_new_measurements={this.props.nr_new_measurements}
            readOnly={this.props.readOnly}
            reload={this.props.reload}
            report={this.props.report}
            report_date={this.props.report_date}
            search_string={this.props.search_string}
            subject_uuid={subject_uuid}
          />
        )}
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
