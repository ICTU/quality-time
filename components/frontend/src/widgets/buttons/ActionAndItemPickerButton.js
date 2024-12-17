import { element, func, string } from "prop-types"
import { useState } from "react"

import { Dropdown, Popup } from "../../semantic_ui_react_wrappers"
import { ItemBreadcrumb } from "../ItemBreadcrumb"

export function ActionAndItemPickerButton({ action, itemType, onChange, get_options, icon }) {
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
                            {icon} {`${action} ${itemType} `}
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
    icon: element,
}
