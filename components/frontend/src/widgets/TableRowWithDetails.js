import "./TableRowWithDetails.css"

import { bool, func, object } from "prop-types"

import { Button, Icon, Table } from "../semantic_ui_react_wrappers"
import { childrenPropType } from "../sharedPropTypes"

export function TableRowWithDetails(props) {
    const { children, details, expanded, onExpand, style, ...otherProps } = props
    return (
        <>
            <Table.Row {...otherProps}>
                <Table.Cell collapsing textAlign="center" style={style}>
                    <Button
                        aria-label="Expand/collapse"
                        basic
                        className="expandcollapse"
                        icon={<Icon name={expanded ? "caret down" : "caret right"} size="large" />}
                        onClick={() => onExpand(!expanded)}
                    />
                </Table.Cell>
                {children}
            </Table.Row>
            {expanded && (
                <Table.Row>
                    <Table.Cell colSpan="99">{details}</Table.Cell>
                </Table.Row>
            )}
        </>
    )
}
TableRowWithDetails.propTypes = {
    children: childrenPropType,
    details: childrenPropType,
    expanded: bool,
    onExpand: func,
    style: object,
}
