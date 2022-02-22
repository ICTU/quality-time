import React from 'react';
import { Table } from '../semantic_ui_react_wrappers/Table';

export function SortableTableHeaderCell({ colSpan, column, sortColumn, sortDirection, handleSort, label, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
        <Table.HeaderCell colSpan={colSpan} onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
            {label}
        </Table.HeaderCell>
    )
}
