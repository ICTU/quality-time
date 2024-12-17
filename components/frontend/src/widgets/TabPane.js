import "./TabPane.css"

import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import { bool, element, oneOfType, string } from "prop-types"
import { useContext } from "react"
import { Menu } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { Label, Tab } from "../semantic_ui_react_wrappers"

function FocusableTab({ error, icon, image, label, warning }) {
    const className = useContext(DarkMode) ? "tabbutton inverted" : "tabbutton"
    let tabLabel = label
    if (error || warning) {
        const color = error ? "red" : "yellow"
        tabLabel = <Label color={color}>{label}</Label>
    }
    return (
        <>
            {icon || image}&nbsp;<button className={className}>{tabLabel}</button>
        </>
    )
}
FocusableTab.propTypes = {
    error: bool,
    icon: element,
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
                    icon={options?.icon}
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
    return tabPane("Configuration", pane, { ...options, icon: <SettingsIcon /> })
}

export function changelogTabPane(pane, options) {
    return tabPane("Changelog", pane, { ...options, icon: <HistoryIcon /> })
}
