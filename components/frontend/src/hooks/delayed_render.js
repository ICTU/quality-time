import { useEffect, useState } from "react"

export function useDelayedRender() {
    const [visible, setVisible] = useState(false)
    useEffect(() => {
        const timeout = setTimeout(setVisible, 50, true)
        return () => clearTimeout(timeout)
    }, [])
    return visible
}
