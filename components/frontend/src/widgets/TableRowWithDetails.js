import React from 'react';
import { Icon, Table } from '../semantic_ui_react_wrappers';

export function TableRowWithDetails(props) {
    var { children, details, expanded, onExpand, style, ...otherProps } = props;
    return (
        <>
            <Table.Row {...otherProps}>
                <Table.Cell
                    collapsing
                    onClick={() => onExpand(!expanded)}
                    onKeyPress={() => onExpand(!expanded)}
                    tabIndex="0"
                    textAlign="center"
                    style={style}
                    role="button"
                >
                    <Icon size='large' name={expanded ? "caret down" : "caret right"} />
                </Table.Cell>
                {children}
            </Table.Row>
            {expanded &&
                <Table.Row>
                    <Table.Cell colSpan="99">
                        {details}
                    </Table.Cell>
                </Table.Row>}
        </>
    );
}
