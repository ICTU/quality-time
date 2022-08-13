import React from 'react';
import { Popup, Table } from '../semantic_ui_react_wrappers';

function TableHeaderCellContents({ help, label }) {
    return help ? <Popup wide="very" trigger={<span>{label}</span>} header={label} hoverable content={help} on={["hover"]} /> : label
}

export function SortableTableHeaderCell({ colSpan, column, sortColumn, sortDirection, handleSort, label, textAlign, help }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
        <Table.HeaderCell colSpan={colSpan} onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
            <TableHeaderCellContents help={help} label={label} />
        </Table.HeaderCell>
    )
}

export function UnsortableTableHeaderCell({ help, label, textAlign, width }) {
    return (
        <Table.HeaderCell className="unsortable" textAlign={textAlign} width={width}>
            <TableHeaderCellContents help={help} label={label} />
        </Table.HeaderCell>
    )
}
