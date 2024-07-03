import { string } from "prop-types"
import { useContext } from "react"
import { Icon as SemanticUIIcon } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"

export function Icon(props) {
    let { className, name, ...otherProps } = props
    /* Using name="linegraph" results in "Invalid prop `name` of value `linegraph` supplied to `Icon`."
       Using name="line graph" does not show the icon. Using className works around this. */
    if (name === "linegraph") {
        className = className ?? ""
        className += ` ${name}`
        name = ""
    }
    return <SemanticUIIcon className={className} inverted={useContext(DarkMode)} name={name} {...otherProps} />
}
Icon.propTypes = {
    className: string,
    name: string,
}
