import React from 'react';
import { Segment } from 'semantic-ui-react';

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
