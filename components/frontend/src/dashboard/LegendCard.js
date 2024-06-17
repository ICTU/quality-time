import "./LegendCard.css"

import { useContext } from "react"
import { List } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { StatusIcon } from "../measurement/StatusIcon"
import { STATUS_SHORT_NAME, STATUSES } from "../metric/status"
import { Card } from "../semantic_ui_react_wrappers"

export function LegendCard() {
    const darkMode = useContext(DarkMode)
    const color = darkMode ? "white" : "black"
    const listItems = STATUSES.map((status) => (
        <List.Item key={status}>
            <List.Icon>
                <StatusIcon status={status} size="small" />
            </List.Icon>
            <List.Content verticalAlign="middle" style={{ color: color }}>
                {STATUS_SHORT_NAME[status]}
            </List.Content>
        </List.Item>
    ))
    return (
        <Card tabIndex="0" className="legend">
            <Card.Content>
                <Card.Header title={"Legend"} textAlign="center">
                    {"Legend"}
                </Card.Header>
                <List size="small">{listItems}</List>
            </Card.Content>
        </Card>
    )
}
