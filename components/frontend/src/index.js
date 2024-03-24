import "fomantic-ui-css/semantic.min.css"
import "react-grid-layout/css/styles.css"
import "react-resizable/css/styles.css"

import { createRoot } from "react-dom/client"

import App from "./App"

const root = createRoot(document.getElementById("root"))
root.render(<App />)
