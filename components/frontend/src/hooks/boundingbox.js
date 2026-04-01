import { useEffect, useRef, useState } from "react"

export const useBoundingBox = () => {
    const ref = useRef()
    const [boundingBox, setBoundingBox] = useState({})
    const timeoutIdsRef = useRef([])

    const getBoundingBox = () => ref.current?.getBoundingClientRect() ?? {}

    useEffect(() => {
        // As we don't know how long animations after a resize or full screen event take,
        // we schedule several timeouts to recalculate the bounding box:
        const timeoutDelays = [0, 250, 500, 750, 1000]
        const clearTimeouts = () => {
            while (timeoutIdsRef.current.length > 0) {
                clearTimeout(timeoutIdsRef.current.pop())
            }
        }

        const set = () => {
            clearTimeouts()
            for (const delay of timeoutDelays) {
                // eslint-disable-next-line @eslint-react/web-api-no-leaked-timeout -- Timeouts are cleaned by clearTimeouts
                timeoutIdsRef.current.push(setTimeout(() => setBoundingBox(getBoundingBox()), delay))
            }
        }

        set()
        globalThis.addEventListener("resize", set)
        globalThis.addEventListener("fullscreenchange", set)
        return () => {
            clearTimeouts()
            globalThis.removeEventListener("resize", set)
            globalThis.removeEventListener("fullscreenchange", set)
        }
    }, [])

    return [boundingBox, ref]
}
