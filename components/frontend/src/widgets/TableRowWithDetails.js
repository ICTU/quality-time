import React, { useState } from 'react';
import { Icon, Table } from 'semantic-ui-react';

export function TableRowWithDetails(props) {
    var { children, details, expanded, onExpand, style, ...otherProps } = props;
    const [show_details, setShowDetails] = useState(expanded);
    function toggleDetails() {
        setShowDetails(!show_details);
        if (props.onExpand) {
            props.onExpand(!show_details)
        }
    }
    return (
        <>
            <Table.Row {...otherProps}>
                <Table.Cell
                    collapsing
                    onClick={() => toggleDetails()}
                    onKeyPress={() => toggleDetails()}
                    tabIndex="0"
                    textAlign="center"
                    style={style}
                    role="button"
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
