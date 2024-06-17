import "./FilterCardWithTable.css"

import { bool, func, string } from "prop-types"

import { Card, Header, Table } from "../semantic_ui_react_wrappers"
import { childrenPropType } from "../sharedPropTypes"
import { FilterCard } from "./FilterCard"

export function FilterCardWithTable({ children, onClick, selected, title }) {
    return (
        <FilterCard onClick={onClick} selected={selected}>
            <Card.Content>
                <Header as="h3" className={selected ? "selected" : null} textAlign="center">
                    {title}
                </Header>
                <Table basic="very" compact="very" size="small">
                    <Table.Body>{children}</Table.Body>
                </Table>
            </Card.Content>
        </FilterCard>
    )
}
FilterCardWithTable.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
    title: string,
}
