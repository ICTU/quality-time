import "./Tag.css"

import { bool, string } from "prop-types"
import { useContext } from "react"
import { Label } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"

export function Tag({ selected, tag }) {
    const defaultColor = useContext(DarkMode) ? "grey" : null
    const color = selected ? "blue" : defaultColor
    return (
        <Label color={color} tag>
            {tag}
        </Label>
    )
}
Tag.propTypes = {
    selected: bool,
    tag: string,
}
