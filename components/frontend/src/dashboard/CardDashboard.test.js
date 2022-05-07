import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';

it('returns null without cards', () => {
    const { container } = render(<CardDashboard cards={[]} />);
    expect(container.children.length).toBe(0)
});

it('does not save the layout after click', async () => {
    const mockCallback = jest.fn();
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <CardDashboard
                cards={[<MetricSummaryCard header="Card" red={1} green={2} yellow={1} white={0} grey={0} />]}
                initial_layout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                save_layout={mockCallback}
            />
        </Permissions.Provider>
    );
    fireEvent.click(screen.getByText("Card"));
    expect(mockCallback).not.toHaveBeenCalled();
})
