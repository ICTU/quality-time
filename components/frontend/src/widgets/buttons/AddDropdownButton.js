import { array, arrayOf, bool, func, string } from "prop-types"
import { useState } from "react"
import { Input } from "semantic-ui-react"

import { Checkbox, Dropdown, Popup } from "../../semantic_ui_react_wrappers"
import { AddItemIcon } from "../icons"

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

export function AddDropdownButton({ itemSubtypes, itemType, onClick, allItemSubtypes, usedItemSubtypeKeys, sort }) {
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
    // Unless specified not to, sort the options:
    if (sort !== false) {
        options.sort((a, b) => a.text.localeCompare(b.text))
    }
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
                            <AddItemIcon /> {`Add ${itemType} `}
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
    sort: bool,
    usedItemSubtypeKeys: arrayOf(string),
}
