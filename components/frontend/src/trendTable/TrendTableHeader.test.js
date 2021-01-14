import React from 'react';
import { fireEvent, render } from '@testing-library/react';
import { TrendTableHeader } from './TrendTableHeader';
import { Dropdown } from 'semantic-ui-react';

describe("TrendTableHeader", () => {
    const dates = [
        new Date("2020-01-03T00:00:00+00:00"),
        new Date("2020-01-05T00:00:00+00:00"),
        new Date("2020-01-09T00:00:00+00:00"),
    ]
    const mockSetInterval = jest.fn()
    const mockSetNrDates = jest.fn()

    it('Renders title bar', () => {
    
        const { queryAllByText, queryAllByRole } = render(
          <table>
            <TrendTableHeader 
                columnDates={dates} 
                trendTableNrDates={2} 
                setTrendTableNrDates={mockSetNrDates} 
                trendTableInterval={2} 
                setTrendTableInterval={mockSetInterval}/>
        </table>
        );

        // header cells
        expect(queryAllByRole("listbox").length).toBe(1) // hamburger dropdown menu
        dates.forEach(date => {
            expect(queryAllByText(date.toLocaleDateString()).length).toBe(1)
        })
        expect(queryAllByText("Unit").length).toBe(1)
    });

    it('Renders the hamburger menu', () => {
        const { queryAllByText, getByRole, getByText } = render(
          <table>
            <TrendTableHeader 
                extraHamburgerItems={<Dropdown.Item>test item</Dropdown.Item>} 
                columnDates={dates} 
                trendTableNrDates={2} 
                setTrendTableNrDates={mockSetNrDates} 
                trendTableInterval={2} 
                setTrendTableInterval={mockSetInterval}/>
        </table>
        );

        // no menu yet
        expect(getByRole("listbox").classList.contains("visible")).toBe(false)

        fireEvent.click(getByRole("listbox"))

        // menu should be visible
        expect(getByRole("listbox").classList.contains("visible")).toBe(true)

        expect(queryAllByText("Number of dates").length).toBe(1)
        const menuItems = ["test item", "Number of dates", "2", "3", "4", "5", "6", "7", "Time between dates", "1 week", "2 weeks", "3 weeks", "4 weeks"]
        menuItems.forEach(number => {
            expect(queryAllByText(number).length).toBe(1)
        })

        expect(getByText("2").classList.contains("active")).toBe(true)
        expect(getByText("2 weeks").classList.contains("active")).toBe(true)

        // hide menu again
        fireEvent.click(getByRole("listbox"))
        expect(getByRole("listbox").classList.contains("visible")).toBe(false)
    });


    it('Calls state changing methods', () => {
        const { getByText, getByRole } = render(
          <table>
            <TrendTableHeader 
                columnDates={dates} 
                trendTableNrDates={2} 
                setTrendTableNrDates={mockSetNrDates} 
                trendTableInterval={2} 
                setTrendTableInterval={mockSetInterval}/>
        </table>
        );

        fireEvent.click(getByRole("listbox"))

        // press nr of dates button
        fireEvent.click(getByText("4"))
        expect(mockSetNrDates).toBeCalled()
        expect(mockSetNrDates.mock.calls[0][0]).toBe(4)
        expect(getByRole("listbox").classList.contains("visible")).toBe(false)


        fireEvent.click(getByRole("listbox"))

        // press nr of dates button
        fireEvent.click(getByText("4 weeks"))
        expect(mockSetInterval).toBeCalled()
        expect(mockSetInterval.mock.calls[0][0]).toBe(4)
        expect(getByRole("listbox").classList.contains("visible")).toBe(false)
    });
})
