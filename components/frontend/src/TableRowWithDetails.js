import React, { Component } from 'react';
import { Icon, Table } from 'semantic-ui-react';

export class TableRowWithDetails extends Component {
  constructor(props) {
    super(props);
    this.state = { show_details: props.show_details };
  }
  expand_or_collapse = (event) => {
    event.preventDefault();
    this.setState((state) => ({ show_details: !state.show_details }));
  };
  render() {
    var { children, show_details, details, ...otherProps } = this.props;
    return (<>
      <Table.Row {...otherProps}>
        <Table.Cell
          collapsing
          onClick={this.expand_or_collapse}
          onKeyPress={this.expand_or_collapse}
          tabIndex="0"
          textAlign="center"
        >
          <Icon size='large' name={this.state.show_details ? "caret down" : "caret right"} />
        </Table.Cell>
        {children}
      </Table.Row>
      {this.state.show_details &&
        <Table.Row>
          <Table.Cell colSpan="99">
            {details}
          </Table.Cell>
        </Table.Row>}
    </>);
  }
}
