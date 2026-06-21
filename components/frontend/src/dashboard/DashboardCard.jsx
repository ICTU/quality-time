import { Card, CardActionArea, CardContent, CardHeader, Tooltip } from "@mui/material"
import { bool, element, func, oneOfType, string } from "prop-types"
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react"

import { childrenPropType } from "../sharedPropTypes"

export function DashboardCard({ children, onClick, selected, title, titleFirst }) {
    const color = selected ? "info.main" : "divider"
    const titleRef = useRef(null)
    const [isTruncated, setIsTruncated] = useState(false)
    const measureTitle = useCallback(() => {
        const el = titleRef.current
        const truncated = Boolean(el) && el.scrollWidth > el.clientWidth
        // Measuring truncation requires reading the laid-out DOM and updating state; the guard keeps it to a single
        // extra render, only when the truncation actually changes.
        // eslint-disable-next-line @eslint-react/set-state-in-effect -- intentional measure-then-set, guarded above
        setIsTruncated((wasTruncated) => (wasTruncated === truncated ? wasTruncated : truncated))
    }, [])
    // Recompute after each render (e.g. when the title changes) and whenever the window is resized.
    useLayoutEffect(measureTitle)
    useEffect(() => {
        globalThis.addEventListener("resize", measureTitle)
        globalThis.addEventListener("fullscreenchange", measureTitle)
        return () => {
            globalThis.removeEventListener("resize", measureTitle)
            globalThis.removeEventListener("fullscreenchange", measureTitle)
        }
    }, [measureTitle])
    const cardHeader = (
        <CardHeader
            title={title}
            slotProps={{
                // The selected class is for test purposes only.
                title: {
                    className: selected ? "selected" : "",
                    noWrap: true,
                    ref: titleRef,
                    variant: "h6",
                    // Hide Safari's native tooltip on truncated text (it ignores an empty title); the MUI tooltip
                    // below replaces it with consistent cross-browser behavior. The card stays clickable because the
                    // CardActionArea ancestor still receives the events that fall through the title.
                    sx: { pointerEvents: "none" },
                },
                content: { sx: { minWidth: 0 } }, // Without min-width: 0 the title overflows instead of truncating
            }}
            sx={{
                padding: "0px",
                paddingTop: titleFirst ? "10px" : "0px",
                textAlign: "center",
                verticalAlign: "center",
            }}
        />
    )
    // Long titles are truncated with an ellipsis (noWrap); show the full title in a tooltip, but only when it's a
    // string that is actually truncated, so cards with short titles don't get a redundant tooltip.
    const header =
        typeof title === "string" && isTruncated ? (
            <Tooltip placement="top" title={title}>
                <div>{cardHeader}</div>
            </Tooltip>
        ) : (
            cardHeader
        )
    // The components below get a height of 100% to make sure they fill the available space of their container
    return (
        <Card
            onClick={onClick}
            sx={{
                border: 1,
                borderColor: color,
                height: "100%",
                "&:hover": { boxShadow: "4", borderColor: "text.primary" },
            }}
        >
            <CardActionArea disableRipple={!onClick} sx={{ height: "100%" }}>
                <CardContent sx={{ paddingBottom: titleFirst ? "0px" : "10px", paddingTop: "0px", height: "100%" }}>
                    {titleFirst && header}
                    {children}
                    {!titleFirst && header}
                </CardContent>
            </CardActionArea>
        </Card>
    )
}
DashboardCard.propTypes = {
    children: childrenPropType,
    onClick: func,
    selected: bool,
    title: oneOfType([element, string]),
    titleFirst: bool,
}
