import { bool, func, object } from "prop-types"

import { Table } from "../semantic_ui_react_wrappers"
import { childrenPropType } from "../sharedPropTypes"
import { ExpandButton } from "./buttons/ExpandButton"

export function TableRowWithDetails(props) {
    const { children, details, expanded, onExpand, style, ...otherProps } = props
    return (
        <>
            <Table.Row {...otherProps}>
                <Table.Cell collapsing textAlign="center" style={style}>
                    <ExpandButton expand={expanded} onClick={() => onExpand(!expanded)} size="1.5em" />
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
