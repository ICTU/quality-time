import React from 'react';
import { render, screen } from '@testing-library/react';
import { CommentSegment } from './CommentSegment';

it("shows the comment", () => {
    render(<CommentSegment comment="Comment" />)
    expect(screen.getByText(/Comment/)).not.toBe(null)
})

it("doesn't show the comment if it's empty", () => {
    const {container } = render(<CommentSegment />)
    expect(container.children.length).toBe(0)
})
