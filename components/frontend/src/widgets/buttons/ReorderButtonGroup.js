import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown"
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp"
import KeyboardDoubleArrowDownIcon from "@mui/icons-material/KeyboardDoubleArrowDown"
import KeyboardDoubleArrowUpIcon from "@mui/icons-material/KeyboardDoubleArrowUp"
import { Button, ButtonGroup, Tooltip } from "@mui/material"
import { bool, element, func, string } from "prop-types"

function ReorderButton(props) {
    const label = `Move ${props.moveable} to the ${props.direction} ${props.slot || "position"}`
    const disabled =
        (props.first && (props.direction === "first" || props.direction === "previous")) ||
        (props.last && (props.direction === "last" || props.direction === "next"))
    return (
        <Tooltip title={label}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    aria-label={label}
                    disabled={disabled}
                    onClick={() => props.onClick(props.direction)}
                    variant="outlined"
                >
                    {props.icon}
                </Button>
            </span>
        </Tooltip>
    )
}
ReorderButton.propTypes = {
    direction: string,
    first: bool,
    icon: element,
    last: bool,
    moveable: string,
    onClick: func,
    slot: string,
}

export function ReorderButtonGroup(props) {
    return (
        <ButtonGroup variant="outlined">
            <ReorderButton {...props} direction="first" icon={<KeyboardDoubleArrowUpIcon />} />
            <ReorderButton {...props} direction="previous" icon={<KeyboardArrowUpIcon />} />
            <ReorderButton {...props} direction="next" icon={<KeyboardArrowDownIcon />} />
            <ReorderButton {...props} direction="last" icon={<KeyboardDoubleArrowDownIcon />} />
        </ButtonGroup>
    )
}
