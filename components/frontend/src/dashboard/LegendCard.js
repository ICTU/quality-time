import React, { useContext } from 'react';
import { List } from 'semantic-ui-react';
import { Card } from '../semantic_ui_react_wrappers';
import { DarkMode } from "../context/DarkMode";
import { StatusIcon } from '../measurement/StatusIcon';
import { getStatusName, STATUSES } from '../utils';
import './LegendCard.css';

export function LegendCard() {
    const darkMode = useContext(DarkMode)
    const color = darkMode ? "white" : "black"
    const listItems = STATUSES.map(status =>
        <List.Item key={status}>
            <List.Icon>
                <StatusIcon status={status} size="small" />
            </List.Icon>
            <List.Content verticalAlign="middle" style={{ color: color }}>
                {getStatusName(status)}
            </List.Content>
        </List.Item>
    );
    return (
        <Card tabIndex="0" className="legend">
            <Card.Content>
                <Card.Header title={"Legend"} textAlign='center'>{"Legend"}</Card.Header>
                <List size="small">
                    {listItems}
                </List>
            </Card.Content>
        </Card>
    )
}
