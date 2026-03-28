import { Box, Typography } from "@mui/material"
import { string } from "prop-types"

export function CommentSegment({ comment }) {
    if (comment) {
        return (
            <Box sx={{ margin: "12px" }}>
                {/* eslint-disable-next-line @eslint-react/dom/no-dangerously-set-innerhtml -- HTML content from backend */}
                <Typography color="text.primary" dangerouslySetInnerHTML={{ __html: comment }} />
            </Box>
        )
    }
    return null
}
CommentSegment.propTypes = {
    comment: string,
}
