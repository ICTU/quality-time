import React from 'react';
import { Segment } from '../semantic_ui_react_wrappers';

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
