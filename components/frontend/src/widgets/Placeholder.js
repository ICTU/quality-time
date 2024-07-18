import { number } from "prop-types"
import { useContext } from "react"
import { Placeholder, PlaceholderImage } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"

export function LoadingPlaceHolder({ height }) {
    const darkMode = useContext(DarkMode)
    const defaultHeight = 400
    return (
        <Placeholder fluid inverted={darkMode} style={{ height: height ?? defaultHeight }}>
            <PlaceholderImage />
        </Placeholder>
    )
}
LoadingPlaceHolder.propTypes = {
    height: number,
}
