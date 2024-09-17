import SellOutlinedIcon from "@mui/icons-material/SellOutlined"
import { Chip } from "@mui/material"
import { bool, string } from "prop-types"

export function Tag({ selected, tag }) {
    const color = selected ? "primary" : ""
    return <Chip color={color} icon={<SellOutlinedIcon />} label={tag} />
}
Tag.propTypes = {
    selected: bool,
    tag: string,
}
