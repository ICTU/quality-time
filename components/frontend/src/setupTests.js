import "@testing-library/jest-dom"

const error = console.error
console.error = (...args) => {
    if (/Support for defaultProps will be removed from function components/.test(args[0])) return
    if (/findDOMNode is deprecated and will be removed in the next major release./.test(args[0])) return
    error(...args)
}
