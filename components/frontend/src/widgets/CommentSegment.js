import { Box, Typography } from "@mui/material"
import { string } from "prop-types"

export function CommentSegment({ comment }) {
    if (comment) {
        return (
            <Box sx={{ margin: "12px" }}>
                <Typography color="text.primary" dangerouslySetInnerHTML={{ __html: comment }} />
            </Box>
        )
    }
    return null
}
CommentSegment.propTypes = {
    comment: string,
}
