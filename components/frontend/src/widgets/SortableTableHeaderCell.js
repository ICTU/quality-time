import React from 'react';
import { Table } from 'semantic-ui-react';

export function SortableTableHeaderCell({ colSpan, column, sortColumn, sortDirection, handleSort, label, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
        <Table.HeaderCell colSpan={colSpan} onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
            {label}
        </Table.HeaderCell>
    )
}
