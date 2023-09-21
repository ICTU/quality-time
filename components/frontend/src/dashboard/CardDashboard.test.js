import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';

it('returns null without cards', () => {
    const { container } = render(<CardDashboard cards={[]} />);
    expect(container.children.length).toBe(0)
});

it('adds the card to the dashboard', () => {
    const { container } = render(
        <CardDashboard
            cards={[<MetricSummaryCard key="card" header="Card" summary={{ "date": { "blue": 0, "red": 1, "green": 2, "yellow": 1, "white": 0, "grey": 0 } }} />]}
            initialLayout={[]}
        />
    );
    expect(container.children.length).toBe(1)
});

it('does not save the layout after click', async () => {
    const mockCallback = jest.fn();
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <CardDashboard
                cards={[<MetricSummaryCard key="card" header="Card" summary={{ "date": { "blue": 0, "red": 1, "green": 2, "yellow": 1, "white": 0, "grey": 0 } }} />]}
                initialLayout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                saveLayout={mockCallback}
            />
        </Permissions.Provider>
    );
    fireEvent.click(screen.getByText("Card"));
    expect(mockCallback).not.toHaveBeenCalled();
})
