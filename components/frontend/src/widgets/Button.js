import { useRef, useState } from "react"
import { array, bool, func, string } from "prop-types"
import { Icon, Input } from "semantic-ui-react"
import { Button, Dropdown, Label, Popup } from "../semantic_ui_react_wrappers"
import { showMessage } from "../widgets/toast"
import { ItemBreadcrumb } from "./ItemBreadcrumb"
import { popupContentPropType } from "../sharedPropTypes"

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
    return (
        <Popup
            content={popup}
            on={["focus", "hover"]}
            position={position || "top left"}
            trigger={button}
        />
    )
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

export function AddDropdownButton({ itemSubtypes, itemType, onClick }) {
    const [selectedItem, setSelectedItem] = useState(0) // Index of selected item in the dropdown
    const [query, setQuery] = useState("") // Search query to filter item subtypes
    const [menuOpen, setMenuOpen] = useState(false) // Is the menu open?
    const [popupTriggered, setPopupTriggered] = useState(false) // Is the popup triggered by hover or focus?
    const options = itemSubtypes.filter((itemSubtype) =>
        itemSubtype.text.toLowerCase().includes(query.toLowerCase()),
    )
    const inputRef = useRef(null)
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
                    onBlur={() => setQuery("")}
                    onClose={() => setMenuOpen(false)}
                    onKeyDown={(event) => {
                        if (!menuOpen) {
                            return
                        }
                        if (event.key === "Escape") {
                            setQuery("")
                        }
                        if (inputRef.current?.inputRef?.current !== document.activeElement) {
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
                            event.target
                                .querySelectorAll("[role='option']")
                                [newIndex]?.scrollIntoView({ block: "nearest" })
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
                    <Dropdown.Menu>
                        <Dropdown.Header>{`Available ${itemType} types`}</Dropdown.Header>
                        {itemSubtypes.length > 5 && (
                            <>
                                <Dropdown.Divider />
                                <Input
                                    className="search"
                                    focus
                                    icon="search"
                                    iconPosition="left"
                                    onChange={(_event, { value }) => setQuery(value)}
                                    onClick={(event) => {
                                        event.stopPropagation()
                                    }}
                                    onKeyDown={(event) => {
                                        if (event.key === " ") {
                                            event.stopPropagation() // Prevent space from closing menu
                                        }
                                    }}
                                    ref={inputRef}
                                    placeholder={`Filter available ${itemType} types`}
                                    value={query}
                                />
                            </>
                        )}
                        <Dropdown.Menu scrolling>
                            {options.map((option, index) => (
                                <Dropdown.Item
                                    key={option.key}
                                    onClick={(_event, { value }) => onClick(value)}
                                    selected={selectedItem === index}
                                    {...option}
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
    itemSubtypes: array,
    itemType: string,
    onClick: func,
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
    const icon = { first: "double up", last: "double down", previous: "up", next: "down" }[
        props.direction
    ]
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
        <Button.Group style={{ marginTop: "0px" }}>
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

export function PermLinkButton({ url }) {
    if (navigator.clipboard) {
        // Frontend runs in a secure context (https) so we can use the Clipboard API
        return (
            <Button
                as="div"
                labelPosition="right"
                onClick={() =>
                    navigator.clipboard.writeText(url).then(
                        function () {
                            showMessage("success", "Copied URL to clipboard")
                        },
                        function () {
                            showMessage("error", "Failed to copy URL to clipboard")
                        },
                    )
                }
            >
                <Button basic content="Copy" icon="copy" primary />
                <Label as="a" color="blue">
                    {url}
                </Label>
            </Button>
        )
    } else {
        // Frontend does not run in a secure context (https) so we cannot use the Clipboard API, and have
        // to use the deprecated Document.execCommand. As document.exeCommand expects selected text, we also
        // cannot use the Label component but have to use a (read only) input element so we can select the URL
        // before copying it to the clipboard.
        return (
            <Input action actionPosition="left" color="blue" defaultValue={url} fluid readOnly>
                <Button
                    basic
                    color="blue"
                    content="Copy"
                    icon="copy"
                    onClick={() => {
                        let urlText = document.querySelector("#permlink")
                        urlText.select()
                        document.execCommand("copy")
                        showMessage("success", "Copied URL to clipboard")
                    }}
                    style={{ fontWeight: "bold" }}
                />
                <input
                    data-testid="permlink"
                    id="permlink"
                    style={{
                        border: "1px solid rgb(143, 208, 255)",
                        color: "rgb(143, 208, 255)",
                        fontWeight: "bold",
                    }}
                />
            </Input>
        )
    }
}
PermLinkButton.propTypes = {
    url: string,
}
