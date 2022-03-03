export function addInvertedClassNameWhenInDarkMode(props, darkMode) {
    let { className, ...otherProps } = props
    className = className ?? ""
    if (darkMode) {
        className += " inverted"
    }
    return { className: className, ...otherProps }
}
