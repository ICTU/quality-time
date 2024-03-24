import { useId } from "react"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { TextInput } from "./TextInput"
import { permissionsPropType } from "../sharedPropTypes"

export function Comment(props) {
    const labelId = useId()
    return (
        <TextInput
            aria-labelledby={labelId}
            label={<label id={labelId}>Comment</label>}
            placeholder="Enter comments here (HTML allowed; URL's are transformed into links)"
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            {...props}
        />
    )
}
Comment.propTypes = {
    requiredPermissions: permissionsPropType,
}
