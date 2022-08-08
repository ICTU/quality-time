import React from 'react';
import { Popup, Table } from '../semantic_ui_react_wrappers';

export function SortableTableHeaderCell({ colSpan, column, sortColumn, sortDirection, handleSort, label, textAlign, help }) {
    const sorted = sortColumn === column ? sortDirection : null;
    const children = help ? <Popup wide trigger={<span>{label}</span>} header={label} content={help} /> : label
    return (
        <Table.HeaderCell colSpan={colSpan} onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
            {children}
        </Table.HeaderCell>
    )
}
