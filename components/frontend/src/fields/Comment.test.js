import React from 'react';
import { render, screen } from '@testing-library/react';
import { Comment } from './Comment';

it("has the comment label", () => {
    render(<Comment />)
    expect(screen.getAllByText(/Comment/).length).toBe(1)
})
