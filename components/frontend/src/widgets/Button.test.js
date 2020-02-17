import React from 'react';
import { act } from 'react-dom/test-utils';
import { mount, shallow } from 'enzyme';
import { AddButton, CopyButton, DeleteButton, DownloadAsPDFButton, MoveButton, ReorderButtonGroup } from './Button';
import * as fetch_server_api from '../api/fetch_server_api';

describe('<AddButton />', () => {
    it('has the correct label', () => {
        const wrapper = shallow(<AddButton item_type="foo" />);
        expect(wrapper.dive().find("Button").children().at(4).text()).toBe("foo");
    });
});

describe('<CopyButton />', () => {
    it('has the correct label', () => {
        const wrapper = shallow(<CopyButton item_type="baz" />);
        expect(wrapper.dive().find("Button").children().at(4).text()).toBe("baz");
    });
});

describe('<DeleteButton />', () => {
    it('has the correct label', () => {
        const wrapper = shallow(<DeleteButton item_type="bar" />);
        expect(wrapper.dive().find("Button").children().at(4).text()).toBe("bar");
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
        fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ok: false});
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

describe('<MoveButton />', () => {
    it('calls the callback on click', () => {
        const mockCallBack = jest.fn();
        const wrapper = mount(<MoveButton options={[{ key: "1", value: "first", text: "First" }]} onClick={mockCallBack} />);
        wrapper.find("Dropdown").at(0).simulate("click");
        wrapper.find("DropdownItem").at(0).simulate("click");
        expect(mockCallBack).toHaveBeenCalledWith("first");
    });
});