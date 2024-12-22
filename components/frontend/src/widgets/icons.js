import AddIcon from "@mui/icons-material/Add"
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth"
import ContentCopyIcon from "@mui/icons-material/ContentCopy"
import DeleteIcon from "@mui/icons-material/Delete"
import LoopIcon from "@mui/icons-material/Loop"
import MoveDownIcon from "@mui/icons-material/MoveDown"
import OpenInNewIcon from "@mui/icons-material/OpenInNew"
import VisibilityIcon from "@mui/icons-material/Visibility"
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff"
import { string } from "prop-types"

export function AddItemIcon() {
    return <AddIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function CalendarIcon() {
    return <CalendarMonthIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function CaretDown({ size }) {
    return <ArrowDropDownIcon title="expand" sx={{ verticalAlign: "middle", fontSize: size || "2.5em" }} />
}
CaretDown.propTypes = {
    size: string,
}

export function CaretRight({ size }) {
    return <ArrowRightIcon title="expand" sx={{ verticalAlign: "middle", fontSize: size || "2.5em" }} />
}
CaretRight.propTypes = {
    size: string,
}

export function CopyItemIcon() {
    return <ContentCopyIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function DeleteItemIcon() {
    return <DeleteIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function IgnoreIcon() {
    return <VisibilityOffIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function MoveItemIcon() {
    return <MoveDownIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function OpenLink() {
    return <OpenInNewIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function LoadingIcon() {
    return (
        <LoopIcon
            sx={{
                animation: "spin 2s linear infinite",
                "@keyframes spin": {
                    "0%": {
                        transform: "rotate(360deg)",
                    },
                    "100%": {
                        transform: "rotate(0deg)",
                    },
                },
                verticalAlign: "middle",
            }}
        />
    )
}

export function RefreshIcon() {
    return <LoopIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function ShowIcon() {
    return <VisibilityIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function TriangleRightIcon() {
    return <ArrowRightIcon fontSize="medium" sx={{ verticalAlign: "middle" }} />
}
