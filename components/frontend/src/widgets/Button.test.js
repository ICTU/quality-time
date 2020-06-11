import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount, shallow } from 'enzyme';
import { AddButton, CopyButton, DeleteButton, DownloadAsPDFButton, MoveButton, ReorderButtonGroup } from './Button';
import { report_options } from './menu_options';
import * as fetch_server_api from '../api/fetch_server_api';

describe('<AddButton />', () => {
    it('has the correct label', () => {
        const wrapper = mount(<AddButton item_type="foo" />);
        expect(wrapper.find("button").children().at(4).text()).toBe("foo");
    });
});

describe('<DeleteButton />', () => {
    it('has the correct label', () => {
        const wrapper = mount(<DeleteButton item_type="bar" />);
        expect(wrapper.find("button").children().at(4).text()).toBe("bar");
    });
});

const item_types = ["report", "subject", "metric", "source"];

describe('<CopyButton />', () => {
    it('has the correct label', () => {
        item_types.forEach((item_type) => {
            const wrapper = mount(<CopyButton item_type={item_type} />);
            expect(wrapper.find("div.button").children().at(2).text()).toBe(`Copy ${item_type} `);
        });
    });
    it('can be used to select an item', () => {
        item_types.forEach((item_type) => {
            const mockCallBack = jest.fn();
            const wrapper = mount(<CopyButton item_type={item_type} onChange={mockCallBack} get_options={() => { return [{key: "1", text: "Report", value: "1"}] }} />);
            wrapper.find("div.button").simulate("click");
            wrapper.find("DropdownItem").simulate("click");
            expect(mockCallBack).toHaveBeenCalledWith("1");
        });
    });
    it('loads the options just once', () => {
        item_types.forEach((item_type) => {
            const mockCallBack = jest.fn();
            let get_options_called = 0;
            const wrapper = mount(<CopyButton item_type={item_type} onChange={mockCallBack} get_options={() => { get_options_called++; return [{key: "1", text: "Report", value: "1"}] }} />);
            wrapper.find("div.button").simulate("click");
            wrapper.find("DropdownItem").simulate("click");
            wrapper.find("div.button").simulate("click");
            wrapper.find("DropdownItem").simulate("click");
            expect(get_options_called).toBe(1);
        });
    });
});

describe('<MoveButton />', () => {
    it('has the correct label', () => {
        item_types.forEach((item_type) => {
            const wrapper = mount(<MoveButton item_type={item_type} />);
            expect(wrapper.find("div.button").children().at(2).text()).toBe(`Move ${item_type} `);
        });
    });
    it('can be used to select an item', () => {
        item_types.forEach((item_type) => {
            const mockCallBack = jest.fn();
            const wrapper = mount(<MoveButton item_type={item_type} onChange={mockCallBack} get_options={() => { return [{key: "1", text: "Report", value: "1"}] }} />);
            wrapper.find("div.button").simulate("click");
            wrapper.find("DropdownItem").simulate("click");
            expect(mockCallBack).toHaveBeenCalledWith("1");
        });
    });
});

describe('<DownloadAsPDFButton />', () => {
    it('has the correct label', () => {
        const wrapper = shallow(<DownloadAsPDFButton />);
        expect(wrapper.dive().find("Button").children().at(4).text()).toBe("report as pdf");
    });
});

jest.mock("../api/fetch_server_api.js")

const test_report = {
    report_uuid: "report_uuid"
};


describe("<DownloadAsPDFButton/>", () => {
    it('indicates loading on click', () => {
        fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
        const wrapper = mount(<DownloadAsPDFButton report={test_report} />);
        wrapper.find("button").simulate("click");
        expect(wrapper.find("button").hasClass("loading")).toBe(true);
    });
    it('ignores a second click', () => {
        fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
        const wrapper = mount(<DownloadAsPDFButton report={test_report} />);
        wrapper.find("button").simulate("click");
        wrapper.find("button").simulate("click");
        expect(wrapper.find("button").hasClass("loading")).toBe(true);
    });
    it('loading is false after returning pdf', async () => {
        fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue("pdf");
        window.URL.createObjectURL = jest.fn();
        let wrapper;
        await act(async () => {
            wrapper = mount(<DownloadAsPDFButton report={test_report} />);
            wrapper.find("button").simulate("click");
        });
        expect(wrapper.find("button").hasClass("loading")).toBe(false);
    });
    it('loading is false after receiving error', async () => {
        fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false });
        let wrapper;
        await act(async () => {
            wrapper = mount(<DownloadAsPDFButton report={test_report} />);
            wrapper.find("button").simulate("click");
        });
        expect(wrapper.find("button").hasClass("loading")).toBe(false);
    });
});

describe("<ReorderButtonGroup />", () => {
    it('calls the callback on click first', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup onClick={mockCallBack} />);
        wrapper.find("Button").at(0).simulate("click");
        expect(mockCallBack).toHaveBeenCalledWith("first");
    });

    it('does not call the callback on click first when the button group is first', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup first={true} onClick={mockCallBack} />);
        wrapper.find("Button").at(0).simulate("click");
        expect(mockCallBack).not.toHaveBeenCalled();
    });

    it('calls the callback on click previous', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup onClick={mockCallBack} />);
        wrapper.find("Button").at(1).simulate("click");
        expect(mockCallBack).toHaveBeenCalledWith("previous");
    });

    it('does not call the callback on click previous when the button group is first', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup first={true} onClick={mockCallBack} />);
        wrapper.find("Button").at(1).simulate("click");
        expect(mockCallBack).not.toHaveBeenCalled();
    });

    it('calls the callback on click next', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup onClick={mockCallBack} />);
        wrapper.find("Button").at(2).simulate("click");
        expect(mockCallBack).toHaveBeenCalledWith("next");
    });

    it('does not call the callback on click next when the button group is last', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup last={true} onClick={mockCallBack} />);
        wrapper.find("Button").at(2).simulate("click");
        expect(mockCallBack).not.toHaveBeenCalled();
    });

    it('calls the callback on click last', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup onClick={mockCallBack} />);
        wrapper.find("Button").at(3).simulate("click");
        expect(mockCallBack).toHaveBeenCalledWith("last");
    });

    it('does not call the callback on click last when the button group is last', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<ReorderButtonGroup last={true} onClick={mockCallBack} />);
        wrapper.find("Button").at(3).simulate("click");
        expect(mockCallBack).not.toHaveBeenCalled();
    });
})
