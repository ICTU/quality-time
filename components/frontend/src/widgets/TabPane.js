import "./TabPane.css"

import { bool, element, oneOfType, string } from "prop-types"
import { useContext } from "react"
import { Menu } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { Icon, Label, Tab } from "../semantic_ui_react_wrappers"

function FocusableTab({ error, iconName, image, label, warning }) {
    const className = useContext(DarkMode) ? "tabbutton inverted" : "tabbutton"
    let tabLabel = label
    if (error || warning) {
        const color = error ? "red" : "yellow"
        tabLabel = <Label color={color}>{label}</Label>
    }
    return (
        <>
            {iconName ? <Icon name={iconName} size="large" /> : image}
            <button className={className}>{tabLabel}</button>
        </>
    )
}
FocusableTab.propTypes = {
    error: bool,
    iconName: string,
    image: element,
    label: oneOfType([element, string]),
    warning: bool,
}

export function tabPane(label, pane, options) {
    // Return a tab and pane, to be used as follows: <Tab panes=[tabPane(...), tabPane(...)] .../>
    return {
        menuItem: (
            <Menu.Item key={label}>
                <FocusableTab
                    error={options?.error}
                    iconName={options?.iconName}
                    image={options?.image}
                    label={label}
                    warning={options?.warning}
                />
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
