import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { AddButton, CopyButton, DeleteButton, DownloadAsPDFButton, MoveButton, PermLinkButton, ReorderButtonGroup } from './Button';
import * as fetch_server_api from '../api/fetch_server_api';
import * as toast from './toast';

test('AddButton has the correct label', () => {
    render(<AddButton item_type="foo" />);
    expect(screen.getAllByText(/foo/).length).toBe(1);
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

test("DownloadAsPDFButton has the correct label", () => {
    render(<DownloadAsPDFButton />);
    expect(screen.getAllByText(/report as pdf/).length).toBe(1);

});

const test_report = { report_uuid: "report_uuid" };
const history = { location: { search: "" } };

test("DownloadAsPDFButton indicates loading on click", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<DownloadAsPDFButton report={test_report} history={history} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).toContain("loading")
});

test("DownloadAsPDFButton ignotes a second click", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<DownloadAsPDFButton report={test_report} history={history} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).toContain("loading")
});

test("DownloadAsPDFButton stops loading after returning pdf", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue("pdf");
    window.URL.createObjectURL = jest.fn();
    render(<DownloadAsPDFButton report={test_report} history={history} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).not.toContain("loading")
});

test("DownloadAsPDFButton stops loading after receiving error", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false });
    window.URL.createObjectURL = jest.fn();
    render(<DownloadAsPDFButton report={test_report} history={history} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).not.toContain("loading")
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

test('PermLinkButton copies url to clipboard', () => {
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) } });
    render(<PermLinkButton url="https://example.org" />)
    fireEvent.click(screen.getByText(/example.org/));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
});

test("PermLinkButton shows success message", async () => {
    toast.show_message = jest.fn();
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) } });
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/example.org/));
    })
    expect(toast.show_message).toHaveBeenCalledWith("success", "Copied URL to clipboard")
});

test("PermLinkButton shows error message", async () => {
    toast.show_message = jest.fn();
    Object.assign(navigator, { clipboard: { writeText: jest.fn().mockImplementation(() => Promise.reject()) } });
    render(<PermLinkButton url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/example.org/));
    })
    expect(toast.show_message).toHaveBeenCalledWith("error", "Failed to copy URL to clipboard")
});
