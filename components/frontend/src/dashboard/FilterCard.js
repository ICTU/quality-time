import { bool, func } from "prop-types"

import { Card } from "../semantic_ui_react_wrappers"
import { childrenPropType } from "../sharedPropTypes"

export function FilterCard({ children, onClick, selected }) {
    return (
        <Card
            className="filter"
            color={selected ? "blue" : null}
            onClick={onClick}
            onKeyPress={onClick}
            style={{ height: "100%" }}
            tabIndex="0"
        >
            {children}
        </Card>
    )
}
FilterCard.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
}
