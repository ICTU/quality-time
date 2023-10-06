import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { CardDashboard } from './CardDashboard';
import { MetricSummaryCard } from './MetricSummaryCard';
import { mockGetAnimations } from './MockAnimations';

beforeEach(() => mockGetAnimations())

afterEach(() => jest.restoreAllMocks())

it('returns null without cards', () => {
    const { container } = render(
        <div id="dashboard">
            <CardDashboard cards={[]} />
        </div>
    );
    expect(container.children[0].children.length).toBe(0)
});

it('adds the card to the dashboard', () => {
    const { container } = render(
        <div id="dashboard">
            <CardDashboard
                cards={[<MetricSummaryCard key="card" header="Card" summary={{ "date": { "blue": 0, "red": 1, "green": 2, "yellow": 1, "white": 0, "grey": 0 } }} />]}
                initialLayout={[]}
            />
        </div>
    );
    expect(container.children.length).toBe(1)
});

it('does not save the layout after click', async () => {
    const mockCallback = jest.fn();
    render(
        <div id="dashboard">
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <CardDashboard
                    cards={[<MetricSummaryCard key="card" header="Card" summary={{ "date": { "blue": 0, "red": 1, "green": 2, "yellow": 1, "white": 0, "grey": 0 } }} />]}
                    initialLayout={[{ h: 6, w: 4, x: 0, y: 0 }]}
                    saveLayout={mockCallback}
                />
            </Permissions.Provider>
        </div>
    );
    fireEvent.click(screen.getByText("Card"));
    expect(mockCallback).not.toHaveBeenCalled();
})
