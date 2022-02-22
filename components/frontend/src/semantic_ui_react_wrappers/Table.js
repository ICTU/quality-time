import React, { useContext } from 'react';
import { Table as SemanticUITable } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Table(props) {
    return (
        <SemanticUITable inverted={useContext(DarkMode)} {...props} />
    )
}

Table.Body = SemanticUITable.Body
Table.Cell = SemanticUITable.Cell
Table.Header = SemanticUITable.Header
Table.HeaderCell = SemanticUITable.HeaderCell
Table.Row = SemanticUITable.Row
