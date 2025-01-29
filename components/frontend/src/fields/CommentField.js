import { bool, func, string } from "prop-types"

import { TextField } from "./TextField"

export function CommentField({ disabled, id, onChange, value }) {
    return (
        <TextField
            disabled={disabled}
            id={id}
            label="Comment"
            multiline
            onChange={onChange}
            placeholder="Enter comments here (HTML allowed; URL's are transformed into links)"
            value={value}
        />
    )
}
CommentField.propTypes = {
    disabled: bool.isRequired,
    id: string,
    onChange: func,
    value: string,
}
