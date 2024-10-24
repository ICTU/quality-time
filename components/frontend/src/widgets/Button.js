import { array, arrayOf, bool, func, string } from "prop-types"
import { useState } from "react"
import { Icon, Input } from "semantic-ui-react"

import { Button, Checkbox, Dropdown, Popup } from "../semantic_ui_react_wrappers"
import { popupContentPropType } from "../sharedPropTypes"
import { showMessage } from "../widgets/toast"
import { ItemBreadcrumb } from "./ItemBreadcrumb"

function stopEventPropagation(event) {
    event.stopPropagation()
}

function stopEventPropagationOnSpace(event) {
    if (event.key === " ") {
        event.stopPropagation() // Prevent space from closing menu
    }
}

function FilterCheckbox({ label, filter, setFilter }) {
    return (
        <Checkbox
            label={label}
            onChange={() => setFilter(!filter)}
            onClick={stopEventPropagation}
            onKeyDown={stopEventPropagationOnSpace}
            style={{ paddingLeft: "10pt", paddingBottom: "10pt" }}
            tabIndex={0}
            value={filter ? 1 : 0}
        />
    )
}
FilterCheckbox.propTypes = {
    label: string,
    filter: bool,
    setFilter: func,
}

function FilterCheckboxes({
    itemType,
    allowHidingUnsupportedItems,
    showUnsupportedItems,
    setShowUnsupportedItems,
    allowHidingUsedItems,
    hideUsedItems,
    setHideUsedItems,
}) {
    if (!allowHidingUnsupportedItems && !allowHidingUsedItems) {
        return null
    }
    return (
        <span style={{ paddingRight: "12px" }}>
            {allowHidingUnsupportedItems && (
                <FilterCheckbox
                    label={`Select from all ${itemType} types`}
                    filter={showUnsupportedItems}
                    setFilter={setShowUnsupportedItems}
                />
            )}
            {allowHidingUsedItems && (
                <FilterCheckbox
                    label={`Hide ${itemType} types already used`}
                    filter={hideUsedItems}
                    setFilter={setHideUsedItems}
                />
            )}
        </span>
    )
}
FilterCheckboxes.propTypes = {
    itemType: string,
    allowHidingUnsupportedItems: bool,
    showUnsupportedItems: bool,
    setShowUnsupportedItems: func,
    allowHidingUsedItems: bool,
    hideUsedItems: bool,
    setHideUsedItems: func,
}

export function ActionButton(props) {
    const { action, disabled, icon, itemType, floated, fluid, popup, position, ...other } = props
    const label = `${action} ${itemType}`
    // Put the button in a span so that a disabled button can still have a popup
    // See https://github.com/Semantic-Org/Semantic-UI-React/issues/2804
    const button = (
        <span style={{ float: floated ?? "none", display: fluid ? "" : "inline-block" }}>
            <Button basic disabled={disabled} icon fluid={fluid} primary {...other}>
                <Icon name={icon} /> {label}
            </Button>
        </span>
    )
    return <Popup content={popup} on={["focus", "hover"]} position={position || "top left"} trigger={button} />
}
ActionButton.propTypes = {
    action: string,
    disabled: bool,
    icon: string,
    itemType: string,
    floated: string,
    fluid: bool,
    popup: popupContentPropType,
    position: string,
}

export function AddDropdownButton({ itemSubtypes, itemType, onClick, allItemSubtypes, usedItemSubtypeKeys }) {
    const [selectedItem, setSelectedItem] = useState(0) // Index of selected item in the dropdown
    const [query, setQuery] = useState("") // Search query to filter item subtypes
    const [menuOpen, setMenuOpen] = useState(false) // Is the menu open?
    const [popupTriggered, setPopupTriggered] = useState(false) // Is the popup triggered by hover or focus?
    const [inputHasFocus, setInputHasFocus] = useState(false) // Does the input have focus?
    const [showUnsupportedItems, setShowUnsupportedItems] = useState(false) // Show only supported itemSubTypes or also unsupported itemSubTypes?
    const [hideUsedItems, setHideUsedItems] = useState(false) // Hide itemSubTypes already used?
    let items = showUnsupportedItems ? allItemSubtypes : itemSubtypes
    if (hideUsedItems) {
        items = items.filter((item) => !usedItemSubtypeKeys.includes(item.key))
    }
    const options = items.filter((itemSubtype) => itemSubtype.text.toLowerCase().includes(query.toLowerCase()))
    options.sort((a, b) => a.text.localeCompare(b.text))
    return (
        <Popup
            content={`Add a new ${itemType} here`}
            on={["focus", "hover"]}
            onOpen={() => setPopupTriggered(true)}
            onClose={() => setPopupTriggered(false)}
            open={!menuOpen && popupTriggered}
            trigger={
                <Dropdown
                    basic
                    className="button icon primary"
                    floating
                    onClose={() => setMenuOpen(false)}
                    onKeyDown={(event) => {
                        if (!menuOpen) {
                            return
                        }
                        if (event.key === "Escape") {
                            setQuery("")
                        }
                        if (!inputHasFocus) {
                            // Allow for editing the query without the input having focus
                            if (event.key === "Backspace") {
                                setQuery(query.slice(0, query.length - 1))
                            } else if (event.key.length === 1) {
                                setQuery(query + event.key)
                            }
                        }
                        if (options.length === 0) {
                            return
                        }
                        if (event.key === "ArrowUp" || event.key === "ArrowDown") {
                            let newIndex
                            if (event.key === "ArrowUp") {
                                newIndex = Math.max(selectedItem - 1, 0)
                            } else {
                                newIndex = Math.min(selectedItem + 1, options.length - 1)
                            }
                            setSelectedItem(newIndex)
                            const activeMenuItem = event.target.querySelectorAll("[role='option']")[newIndex]
                            activeMenuItem?.scrollIntoView({ block: "nearest" })
                        }
                        if (event.key === "Enter") {
                            onClick(options[selectedItem].value)
                        }
                    }}
                    onOpen={() => setMenuOpen(true)}
                    selectOnBlur={false}
                    selectOnNavigation={false}
                    trigger={
                        <>
                            <Icon name="add" /> {`Add ${itemType} `}
                        </>
                    }
                    value={null} // Without this, a selected item becomes active (shown bold in the menu) and can't be selected again
                >
                    <Dropdown.Menu style={{ minWidth: "50em" }}>
                        <Dropdown.Header>{`Available ${itemType} types`}</Dropdown.Header>
                        <Dropdown.Divider />
                        <Input
                            className="search"
                            focus
                            icon="search"
                            iconPosition="left"
                            onBlur={(event) => {
                                setInputHasFocus(false)
                                if (allItemSubtypes) {
                                    event.stopPropagation()
                                } // Prevent tabbing to the checkbox from clearing the input
                            }}
                            onChange={(_event, { value }) => setQuery(value)}
                            onClick={stopEventPropagation}
                            onFocus={() => {
                                setInputHasFocus(true)
                            }}
                            onKeyDown={stopEventPropagationOnSpace}
                            placeholder={`Filter ${itemType} types`}
                            value={query}
                        />
                        <FilterCheckboxes
                            itemType={itemType}
                            allowHidingUnsupportedItems={allItemSubtypes?.length > 0}
                            showUnsupportedItems={showUnsupportedItems}
                            setShowUnsupportedItems={setShowUnsupportedItems}
                            allowHidingUsedItems={usedItemSubtypeKeys?.length > 0}
                            hideUsedItems={hideUsedItems}
                            setHideUsedItems={setHideUsedItems}
                        />
                        <Dropdown.Menu scrolling>
                            {options.map((option, index) => (
                                <Dropdown.Item
                                    content={option.content}
                                    key={option.key}
                                    onClick={(_event, { value }) => onClick(value)}
                                    selected={selectedItem === index}
                                    style={{ whiteSpace: "wrap" }}
                                    text={option.text}
                                    value={option.value}
                                />
                            ))}
                        </Dropdown.Menu>
                    </Dropdown.Menu>
                </Dropdown>
            }
        />
    )
}
AddDropdownButton.propTypes = {
    allItemSubtypes: array,
    itemSubtypes: array,
    itemType: string,
    onClick: func,
    usedItemSubtypeKeys: arrayOf(string),
}

export function AddButton({ itemType, onClick }) {
    return (
        <ActionButton
            action="Add"
            icon="plus"
            itemType={itemType}
            onClick={() => onClick()}
            popup={`Add a new ${itemType} here`}
        />
    )
}
AddButton.propTypes = {
    itemType: string,
    onClick: func,
}

export function DeleteButton(props) {
    return (
        <ActionButton
            action="Delete"
            floated="right"
            icon="trash"
            negative
            popup={`Delete this ${props.itemType}. Careful, this can only be undone by a system administrator!`}
            position="top right"
            {...props}
        />
    )
}
DeleteButton.propTypes = {
    itemType: string,
}

function ReorderButton(props) {
    const label = `Move ${props.moveable} to the ${props.direction} ${props.slot || "position"}`
    const icon = { first: "double up", last: "double down", previous: "up", next: "down" }[props.direction]
    const disabled =
        (props.first && (props.direction === "first" || props.direction === "previous")) ||
        (props.last && (props.direction === "last" || props.direction === "next"))
    return (
        <Popup
            content={label}
            trigger={
                <Button
                    aria-label={label}
                    basic
                    disabled={disabled}
                    icon={`angle ${icon}`}
                    onClick={() => props.onClick(props.direction)}
                    primary
                />
            }
        />
    )
}
ReorderButton.propTypes = {
    direction: string,
    first: bool,
    last: bool,
    moveable: string,
    onClick: func,
    slot: string,
}

export function ReorderButtonGroup(props) {
    return (
        <Button.Group style={{ marginTop: "0px", marginRight: "5px" }}>
            <ReorderButton {...props} direction="first" />
            <ReorderButton {...props} direction="previous" />
            <ReorderButton {...props} direction="next" />
            <ReorderButton {...props} direction="last" />
        </Button.Group>
    )
}

function ActionAndItemPickerButton({ action, itemType, onChange, get_options, icon }) {
    const [options, setOptions] = useState([])

    const breadcrumbProps = { report: "report" }
    if (itemType !== "report") {
        breadcrumbProps.subject = "subject"
        if (itemType !== "subject") {
            breadcrumbProps.metric = "metric"
            if (itemType !== "metric") {
                breadcrumbProps.source = "source"
            }
        }
    }
    return (
        <Popup
            content={`${action} an existing ${itemType} here`}
            trigger={
                <Dropdown
                    basic
                    className="button icon primary"
                    floating
                    header={
                        <Dropdown.Header>
                            <ItemBreadcrumb size="tiny" {...breadcrumbProps} />
                        </Dropdown.Header>
                    }
                    options={options}
                    onChange={(_event, { value }) => onChange(value)}
                    onOpen={() => setOptions(get_options())}
                    scrolling
                    selectOnBlur={false}
                    selectOnNavigation={false}
                    trigger={
                        <>
                            <Icon name={icon} /> {`${action} ${itemType} `}
                        </>
                    }
                    value={null} // Without this, a selected item becomes active (shown bold in the menu) and can't be selected again
                />
            }
        />
    )
}
ActionAndItemPickerButton.propTypes = {
    action: string,
    itemType: string,
    onChange: func,
    get_options: func,
    icon: string,
}

export function CopyButton(props) {
    return <ActionAndItemPickerButton {...props} action="Copy" icon="copy" />
}

export function MoveButton(props) {
    return <ActionAndItemPickerButton {...props} action="Move" icon="shuffle" />
}

export function PermLinkButton({ itemType, url }) {
    if (window.isSecureContext) {
        // Frontend runs in a secure context (https) so we can use the Clipboard API
        return (
            <Popup
                content={`Copy a permanent link to this ${itemType} to the clipboard`}
                trigger={
                    <Button
                        basic
                        content={`Share ${itemType}`}
                        icon="share square"
                        onClick={() =>
                            navigator.clipboard
                                .writeText(url)
                                .then(() => showMessage("success", "Copied URL to clipboard"))
                                .catch((error) => showMessage("error", "Could not copy URL to clipboard", `${error}`))
                        }
                        primary
                    />
                }
            />
        )
    }
    return null
}
PermLinkButton.propTypes = {
    itemType: string,
    url: string,
}
