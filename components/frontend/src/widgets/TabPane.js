import "./TabPane.css"

import { bool, element, oneOfType, string } from "prop-types"
import { useContext } from "react"
import { Menu } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { Icon, Label, Tab } from "../semantic_ui_react_wrappers"

function FocusableTab({ error, iconName, label }) {
    const className = useContext(DarkMode) ? "tabbutton inverted" : "tabbutton"
    const tabLabel = error ? <Label color="red">{label}</Label> : label
    return (
        <>
            {iconName && <Icon name={iconName} />}
            <button className={className}>{tabLabel}</button>
        </>
    )
}
FocusableTab.propTypes = {
    error: bool,
    iconName: string,
    label: oneOfType([element, string]),
}

export function tabPane(label, pane, options) {
    // Return a tab and pane, to be used as follows: <Tab panes=[tabPane(...), tabPane(...)] .../>
    return {
        menuItem: (
            <Menu.Item key={label}>
                <FocusableTab error={options?.error} iconName={options?.iconName} label={label} />
            </Menu.Item>
        ),
        render: () => <Tab.Pane>{pane}</Tab.Pane>,
    }
}

export function configurationTabPane(pane, options) {
    return tabPane("Configuration", pane, { ...options, iconName: "settings" })
}

export function changelogTabPane(pane, options) {
    return tabPane("Changelog", pane, { ...options, iconName: "history" })
}
