import React, { useState } from 'react';
import { Icon, Table } from 'semantic-ui-react';

export function TableRowWithDetails(props) {
  var { children, show_details, details, ...otherProps } = props;
  const [show_details_state, setShowDetails] = useState(show_details);
  return (
    <>
      <Table.Row {...otherProps}>
        <Table.Cell
          collapsing
          onClick={() => setShowDetails(!show_details_state)}
          onKeyPress={() => setShowDetails(!show_details_state)}
          tabIndex="0"
          textAlign="center"
        >
          <Icon size='large' name={show_details_state ? "caret down" : "caret right"} />
        </Table.Cell>
        {children}
      </Table.Row>
      {show_details_state &&
        <Table.Row>
          <Table.Cell colSpan="99">
            {details}
          </Table.Cell>
        </Table.Row>}
    </>
  );
}
