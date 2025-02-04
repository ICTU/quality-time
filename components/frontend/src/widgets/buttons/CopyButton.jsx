import { CopyItemIcon } from "../icons"
import { ActionAndItemPickerButton } from "./ActionAndItemPickerButton"

export function CopyButton(props) {
    return <ActionAndItemPickerButton {...props} action="Copy" icon={<CopyItemIcon />} />
}
