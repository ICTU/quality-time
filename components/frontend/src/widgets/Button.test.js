import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { AddButton, CopyButton, DeleteButton, DownloadAsPDFButton, MoveButton, ReorderButtonGroup } from './Button';
import * as fetch_server_api from '../api/fetch_server_api';

test('AddButton has the correct label', () => {
    render(<AddButton item_type="foo" />);
    expect(screen.getAllByText(/foo/).length).toBe(1);
});

test('DeleteButton has the correct label', () => {
    render(<DeleteButton item_type="bar" />);
    expect(screen.getAllByText(/bar/).length).toBe(1);
});

const item_types = ["report", "subject", "metric", "source"];

item_types.forEach((item_type) => {
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
        fireEvent.click(screen.getByText(/Item/));
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
        fireEvent.click(screen.getByText(/Item/));
        expect(mockCallBack).toHaveBeenCalledWith("1");
    });
});

test("DownloadAsPDFButton has the correct label", () => {
    render(<DownloadAsPDFButton />);
    expect(screen.getAllByText(/report as pdf/).length).toBe(1);

});

jest.mock("../api/fetch_server_api.js")

const test_report = {
    report_uuid: "report_uuid"
};

test("DownloadAsPDFButton indicates loading on click", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<DownloadAsPDFButton report={test_report} history={{ location: { search: "" } }} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).toContain("loading")
});

test("DownloadAsPDFButton ignotes a second click", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    render(<DownloadAsPDFButton report={test_report} history={{ location: { search: "" } }} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).toContain("loading")
});

test("DownloadAsPDFButton stops loading after returning pdf", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue("pdf");
    window.URL.createObjectURL = jest.fn();
    render(<DownloadAsPDFButton report={test_report} history={{ location: { search: "" } }} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).not.toContain("loading")
});

test("DownloadAsPDFButton stops loading after receiving error", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false });
    window.URL.createObjectURL = jest.fn();
    render(<DownloadAsPDFButton report={test_report} history={{ location: { search: "" } }} />);
    await act(async () => {
        fireEvent.click(screen.getByText(new RegExp(/Download/)));
    });
    expect(screen.getByText(/Download/).className).not.toContain("loading")
});

test("ReorderButtonGroup calls the callback on click first", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the first position"));
    expect(mockCallBack).toHaveBeenCalledWith("first");
});

test('ReorderButtonGroup does not call the callback on click first when the button group is first', () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} first={true} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the first position"));
    expect(mockCallBack).not.toHaveBeenCalled();
});

test("ReorderButtonGroup calls the callback on click previous", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the previous position"));
    expect(mockCallBack).toHaveBeenCalledWith("previous");
});

test("ReorderButtonGroup does not call the callback on click previous when the button group is first", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} first={true} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the previous position"));
    expect(mockCallBack).not.toHaveBeenCalled();
})

test("ReorderButtonGroup calls the callback on click next", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the next position"));
    expect(mockCallBack).toHaveBeenCalledWith("next");
});

test("ReorderButtonGroup does not call the callback on click next when the button group is last", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} last={true} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the next position"));
    expect(mockCallBack).not.toHaveBeenCalled();
});

test("ReorderButtonGroup calls the callback on click last", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the last position"));
    expect(mockCallBack).toHaveBeenCalledWith("last");
});

test("ReorderButtonGroup does not call the callback on click last when the button group is last", () => {
    const mockCallBack = jest.fn();
    render(<ReorderButtonGroup onClick={mockCallBack} last={true} moveable="item" />);
    fireEvent.click(screen.getByLabelText("Move item to the last position"));
    expect(mockCallBack).not.toHaveBeenCalled();
});
