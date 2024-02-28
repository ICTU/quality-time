import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddButton, AddDropdownButton, CopyButton, DeleteButton, MoveButton, PermLinkButton, ReorderButtonGroup } from './Button';
import * as toast from './toast';

function renderAddDropdownButton(nr_items = 2) {
    const mockCallback = jest.fn();
    const item_subtypes = [];
    for (const index of Array(nr_items).keys()) {
        const text = `Sub ${index + 1}`;
        const key = text.toLowerCase();
        item_subtypes.push({ key: key, text: text, value: key })
    }
    render(
        <AddDropdownButton
            item_type="foo"
            item_subtypes={item_subtypes}
            onClick={mockCallback}
        />
    );
    return mockCallback;
}

test('AddDropdownButton mouse navigation', async () => {
    const mockCallBack = renderAddDropdownButton()
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Sub 2/)) });
    expect(mockCallBack).toHaveBeenCalledWith("sub 2")
});

test('AddDropdownButton keyboard navigation', async () => {
    const mockCallBack = renderAddDropdownButton()
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await act(async () => { fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowDown" }) });
    await act(async () => { fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowUp" }) });
    await act(async () => { fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowDown" }) });
    await act(async () => { fireEvent.keyDown(screen.getByText(/Sub 2/), { key: "Enter" }) });
    expect(mockCallBack).toHaveBeenCalledWith("sub 2")
});

test('AddDropdownButton hides popup when dropdown is shown', async () => {
    renderAddDropdownButton()
    await userEvent.hover(screen.getByText(/Add foo/));
    await waitFor(() => { expect(screen.queryAllByText(/Add a new foo here/).length).toBe(1) })
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    expect(screen.queryAllByText(/Add a new foo here/).length).toBe(0);  // Popup should disappear
    await userEvent.type(screen.getByText(/Add foo/), "{Escape}");  // Close dropdown
    await userEvent.hover(screen.getByText(/Add foo/));
    await waitFor(() => { expect(screen.queryAllByText(/Add a new foo here/).length).toBe(1) })  // Popup should appear again
});

test('AddDropdownButton filter one item', async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 6{Enter}");
    expect(mockCallback).toHaveBeenCalledWith("sub 6")
});

test('AddDropdownButton filter one item without focus', async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    const dropdown = screen.getByText(/Add foo/)
    await act(async () => { fireEvent.keyDown(dropdown, { key: "9" }) });
    await act(async () => { fireEvent.keyDown(dropdown, { key: "Backspace" }) });
    await act(async () => { fireEvent.keyDown(dropdown, { key: "6" }) });
    await act(async () => { fireEvent.keyDown(dropdown, { key: "Enter" }) });
    expect(mockCallback).toHaveBeenCalledWith("sub 6")
});

test('AddDropdownButton filter zero items', async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "FOO{Enter}");
    expect(mockCallback).not.toHaveBeenCalled()
});

test('AddDropdownButton resets query on escape', async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "FOO{Escape}");
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await act(async () => { fireEvent.keyDown(screen.getByText(/Sub 1/), { key: "Enter" }) });
    expect(mockCallback).toHaveBeenCalledWith("sub 1")
});

test('AddDropdownButton does not add selected item on enter when menu is closed', async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => { fireEvent.click(screen.getByText(/Add foo/)) });
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub{Escape}");
    await act(async () => { fireEvent.keyDown(screen.getByText(/Add foo/), { key: "Enter" }) });
    expect(mockCallback).not.toHaveBeenCalled()
});

test('AddButton has the correct label', () => {
    render(<AddButton item_type="bar" />);
    expect(screen.getAllByText(/bar/).length).toBe(1);
});

test('DeleteButton has the correct label', () => {
    render(<DeleteButton item_type="bar" />);
    expect(screen.getAllByText(/bar/).length).toBe(1);
});

["report", "subject", "metric", "source"].forEach((item_type) => {
    test('CopyButton has the correct label', () => {
        render(<CopyButton item_type={item_type} />);
        expect(screen.getAllByText(new RegExp(`Copy ${item_type}`)).length).toBe(1);
    });

    test('CopyButton can be used to select an item', async () => {
        const mockCallBack = jest.fn();
        render(<CopyButton item_type={item_type} onChange={mockCallBack} get_options={() => { return [{ key: "1", text: "Item", value: "1" }] }} />);
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${item_type}`)));
        });
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/));
        });
        expect(mockCallBack).toHaveBeenCalledWith("1");
    });

    test("CopyButton loads the options every time the menu is opened", async () => {
        const mockCallBack = jest.fn();
        let get_options_called = 0;
        render(<CopyButton item_type={item_type} onChange={mockCallBack} get_options={() => { get_options_called++; return [{ key: "1", text: "Item", value: "1" }] }} />);
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${item_type}`)));
        });
        fireEvent.click(screen.getByText(/Item/));
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${item_type}`)));
        });
        expect(get_options_called).toBe(2);
    });

    test('MoveButton has the correct label', () => {
        render(<MoveButton item_type={item_type} />);
        expect(screen.getAllByText(new RegExp(`Move ${item_type}`)).length).toBe(1);
    });

    test('MoveButton can be used to select an item', async () => {
        const mockCallBack = jest.fn();
        render(<MoveButton item_type={item_type} onChange={mockCallBack} get_options={() => { return [{ key: "1", text: "Item", value: "1" }] }} />);
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Move ${item_type}`)));
        });
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/));
        });
        expect(mockCallBack).toHaveBeenCalledWith("1");
    });
});

["first", "last", "previous", "next"].forEach((direction) => {
    test("ReorderButtonGroup calls the callback on click direction", async () => {
        const mockCallBack = jest.fn();
        render(<ReorderButtonGroup onClick={mockCallBack} moveable="item" />);
        await act(async () => {
            fireEvent.click(screen.getByLabelText(`Move item to the ${direction} position`));
        })
        expect(mockCallBack).toHaveBeenCalledWith(direction);
    });

    test('ReorderButtonGroup does not call the callback on click direction when the button group is already there', () => {
        const mockCallBack = jest.fn();
        render(<ReorderButtonGroup onClick={mockCallBack} first={true} last={true} moveable="item" />);
        fireEvent.click(screen.getByLabelText(`Move item to the ${direction} position`));
        expect(mockCallBack).not.toHaveBeenCalled();
    });
});

test('PermLinkButton copies url to clipboard if not in a secure context', () => {
    Object.assign(document, { execCommand: jest.fn() })
    render(<PermLinkButton url="https://example.org" />)
    fireEvent.click(screen.getByText(/Copy/));
    expect(document.execCommand).toHaveBeenCalledWith("copy")
});

test("PermLinkButton shows success message if not in a secure context", async () => {
    toast.showMessage = jest.fn();
    Object.assign(document, { execCommand: jest.fn() })
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => { fireEvent.click(screen.getByText(/Copy/)) })
    expect(toast.showMessage).toHaveBeenCalledWith("success", "Copied URL to clipboard")
});

test("PermLinkButton copies URL to clipboard if in a secure context", async () => {
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) } });
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => { fireEvent.click(screen.getByText(/example.org/)) })
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
});

test("PermLinkButton shows success message if in a secure context", async () => {
    toast.showMessage = jest.fn();
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) } });
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => { fireEvent.click(screen.getByText(/example.org/)) })
    expect(toast.showMessage).toHaveBeenCalledWith("success", "Copied URL to clipboard")
});

test("PermLinkButton shows error message if in a secure context", async () => {
    toast.showMessage = jest.fn();
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.reject()) } });
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => { fireEvent.click(screen.getByText(/example.org/)) })
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Failed to copy URL to clipboard")
});
