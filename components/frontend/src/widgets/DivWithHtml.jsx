import "./DivWithHtml.css"

import { useLayoutEffect, useRef, useState } from "react"

import { childrenPropType } from "../sharedPropTypes"

export function DivWithHtml({ children }) {
    const minHeight = 15
    const maxHeight = 60
    const ref = useRef()
    // Keep track of whether the div is overflown, so the resize handle can be hidden when not needed
    const [overflown, setOverflown] = useState(false)
    useLayoutEffect(() => {
        setOverflown(ref.current.clientHeight < ref.current.scrollHeight) // eslint-disable-line @eslint-react/set-state-in-effect -- DOM measurement must happen after layout
    }, [children])
    return (
        <div
            className="with-html"
            ref={ref}
            style={{
                wordBreak: "break-word",
                overflow: overflown ? "auto" : "visible",
                minHeight: minHeight,
                ...(overflown ? { height: maxHeight } : { maxHeight: maxHeight }),
                resize: overflown ? "vertical" : "",
            }}
            // eslint-disable-next-line @eslint-react/dom/no-dangerously-set-innerhtml -- HTML content from backend
            dangerouslySetInnerHTML={{ __html: children }}
        />
    )
}
DivWithHtml.propTypes = {
    children: childrenPropType,
}
