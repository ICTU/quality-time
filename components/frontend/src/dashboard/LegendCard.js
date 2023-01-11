import React from 'react';
import { List } from 'semantic-ui-react';
import { Card } from '../semantic_ui_react_wrappers';
import { StatusIcon } from '../measurement/StatusIcon';
import { getStatuses, getStatusName } from '../utils';

export function LegendCard({ darkMode }) {
    const size = "small"
    const color = darkMode ? "white" : "black"
    const listItems = getStatuses().map(status => {
        return (
            <List.Item key={status}>
                <List.Icon>
                    <StatusIcon status={status} size={size} />
                </List.Icon>
                <List.Content verticalAlign="middle" style={{ color: color }}>
                    {getStatusName(status)}
                </List.Content>
            </List.Item>
        )
    });
    return (
        <Card style={{ height: '200px' }} tabIndex="0">
            <Card.Content>
                <Card.Header title={"Legend"} textAlign='center'>{"Legend"}</Card.Header>
                <List size="small">
                    {listItems}
                </List>
            </Card.Content>
        </Card>
    )
}