import { MoveItemIcon } from "../icons"
import { ActionAndItemPickerButton } from "./ActionAndItemPickerButton"

export function MoveButton(props) {
    return <ActionAndItemPickerButton {...props} action="Move" icon={<MoveItemIcon />} />
}
