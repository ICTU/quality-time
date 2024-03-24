import { Segment } from "../semantic_ui_react_wrappers"
import { string } from "prop-types"

export function CommentSegment({ comment }) {
    if (comment) {
        return (
            <Segment basic style={{ marginTop: "10px" }}>
                <div dangerouslySetInnerHTML={{ __html: comment }} />
            </Segment>
        )
    }
    return null
}
CommentSegment.propTypes = {
    comment: string,
}
