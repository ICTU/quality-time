import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UIModeMenu } from './UIModeMenu';

it("sets dark mode", () => {
    const setUIMode = jest.fn();
    render(<UIModeMenu setUIMode={setUIMode} />)
    fireEvent.click(screen.getByText(/Dark mode/))
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("sets light mode", () => {
    const setUIMode = jest.fn();
    render(<UIModeMenu setUIMode={setUIMode} uiMode="dark" />)
    fireEvent.click(screen.getByText(/Light mode/))
    expect(setUIMode).toHaveBeenCalledWith("light")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = jest.fn();
    render(<UIModeMenu hideMetricsNotRequiringAction={true} setUIMode={setUIMode} />)
    await userEvent.type(screen.getByText(/Dark mode/), " ")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})
