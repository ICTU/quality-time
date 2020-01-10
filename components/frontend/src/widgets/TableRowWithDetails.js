import React, { useState } from 'react';
import { Icon, Table } from 'semantic-ui-react';

export function TableRowWithDetails(props) {
  var { children, details, ...otherProps } = props;
  const [show_details, setShowDetails] = useState(false);
  return (
    <>
      <Table.Row {...otherProps}>
        <Table.Cell
          collapsing
          onClick={() => setShowDetails(!show_details)}
          onKeyPress={() => setShowDetails(!show_details)}
          tabIndex="0"
          textAlign="center"
        >
          <Icon size='large' name={show_details ? "caret down" : "caret right"} />
        </Table.Cell>
        {children}
      </Table.Row>
      {show_details &&
        <Table.Row>
          <Table.Cell colSpan="99">
            {details}
          </Table.Cell>
        </Table.Row>}
    </>
  );
}
