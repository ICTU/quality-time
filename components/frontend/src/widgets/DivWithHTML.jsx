import "./DivWithHTML.css"

import { createRef, useLayoutEffect, useState } from "react"

import { childrenPropType } from "../sharedPropTypes"

export function DivWithHTML({ children }) {
    const minHeight = 15
    const maxHeight = 60
    const ref = createRef()
    // Keep track of whether the div is overflown, so the resize handle can be hidden when not needed
    const [overflown, setOverflown] = useState(false)
    const [scrollHeight, setScrollHeight] = useState(minHeight)
    useLayoutEffect(() => {
        setOverflown(ref.current.clientHeight < ref.current.scrollHeight)
        setScrollHeight(ref.current.scrollHeight)
    }, [ref])
    return (
        <div
            className="with-html"
            ref={ref}
            style={{
                wordBreak: "break-word",
                overflow: "auto",
                minHeight: minHeight,
                height: Math.min(maxHeight, scrollHeight),
                resize: overflown ? "vertical" : "",
            }}
            dangerouslySetInnerHTML={{ __html: children }}
        />
    )
}
DivWithHTML.propTypes = {
    children: childrenPropType,
}
