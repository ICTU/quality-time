import AddIcon from "@mui/icons-material/Add"
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
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

const caretSx = {
    verticalAlign: "middle",
    "@media print": {
        display: "none !important",
    },
}

export function CaretDown({ size }) {
    return <ArrowDropDownIcon title="expand" sx={{ ...caretSx, fontSize: size }} />
}
CaretDown.propTypes = {
    size: string.isRequired,
}

export function CaretRight({ size }) {
    return <ArrowRightIcon title="expand" sx={{ ...caretSx, fontSize: size }} />
}
CaretRight.propTypes = {
    size: string.isRequired,
}

export function CopyItemIcon() {
    return <ContentCopyIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function DeleteItemIcon() {
    return <DeleteIcon fontSize="inherit" sx={{ verticalAlign: "middle" }} />
}

export function IgnoreIcon() {
    return <VisibilityOffIcon className="hide icon" fontSize="inherit" sx={{ verticalAlign: "middle" }} />
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
