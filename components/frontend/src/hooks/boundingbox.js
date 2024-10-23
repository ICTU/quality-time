import { useEffect, useRef, useState } from "react"

export const useBoundingBox = () => {
    const ref = useRef()
    const [boundingBox, setBoundingBox] = useState({})
    // As we don't know how long animations after a resize or full screen event take,
    // we schedule several timeouts to recalculate the bounding box:
    const timeoutDelays = [250, 500, 750, 1000]
    const timeoutIds = []

    const getBoundingBox = () => ref.current?.getBoundingClientRect() ?? {}

    const clearTimeouts = () => {
        while (timeoutIds.length > 0) {
            clearTimeout(timeoutIds.pop())
        }
    }

    const set = () => {
        setBoundingBox(getBoundingBox())
        clearTimeouts()
        timeoutDelays.forEach((delay) => {
            timeoutIds.push(setTimeout(() => setBoundingBox(getBoundingBox()), delay))
        })
    }

    useEffect(() => {
        set()
        window.addEventListener("resize", set)
        window.addEventListener("fullscreenchange", set)
        return () => {
            clearTimeouts()
            window.removeEventListener("resize", set)
            window.removeEventListener("fullscreenchange", set)
        }
    }, [])

    return [boundingBox, ref]
}
