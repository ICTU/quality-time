import { useContext } from "react"
import { Checkbox as SemanticUICheckbox } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"
import { addInvertedClassNameWhenInDarkMode } from "./dark_mode"

export function Checkbox(props) {
    return <SemanticUICheckbox {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
}
