import React from 'react';
import { render, screen } from '@testing-library/react';
import { LabelWithHyperLink } from './LabelWithHyperLink';

it("shows the label", () => {
    render(<LabelWithHyperLink label="Hello" />)
    expect(screen.getByText(/Hello/)).not.toBe(null)
})
