import "fomantic-ui-css/semantic.min.css"
import "react-grid-layout/css/styles.css"

import { createRoot } from "react-dom/client"

import App from "./App"

const error = console.error
console.error = (...args) => {
    if (/Support for defaultProps will be removed from function components/.test(args[0])) return
    if (/findDOMNode is deprecated and will be removed in the next major release./.test(args[0])) return
    error(...args)
}

const root = createRoot(document.getElementById("root"))
root.render(<App />)
