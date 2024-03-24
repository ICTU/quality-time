import "react-datepicker/dist/react-datepicker.css"
import "./DatePicker.css"

import { func } from "prop-types"
import { default as ReactDatePicker } from "react-datepicker"

import { isValidDate_YYYYMMDD } from "../utils"

export function DatePicker(props) {
    const { onChange, ...otherProps } = props
    return (
        <ReactDatePicker
            dateFormat="yyyy-MM-dd"
            dropdownMode="select"
            onChange={(date) => {
                if (date === null) {
                    onChange(null)
                }
            }} // See https://github.com/Hacker0x01/react-datepicker/discussions/3636
            onChangeRaw={(event) => {
                if (isValidDate_YYYYMMDD(event.target.value)) {
                    onChange(new Date(event.target.value))
                }
            }}
            onSelect={onChange}
            placeholderText="YYYY-MM-DD"
            showIcon={false}
            showMonthDropdown
            showPopperArrow={false}
            showYearDropdown
            todayButton="Today"
            {...otherProps}
        />
    )
}
DatePicker.propTypes = {
    onChange: func,
}
