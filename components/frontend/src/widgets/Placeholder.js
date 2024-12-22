import { Skeleton } from "@mui/material"
import { number } from "prop-types"

export function LoadingPlaceHolder({ height }) {
    const defaultHeight = 400
    return <Skeleton animation="wave" height={height ?? defaultHeight} variant="rectangular" />
}
LoadingPlaceHolder.propTypes = {
    height: number,
}
