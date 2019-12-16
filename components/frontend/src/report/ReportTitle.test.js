import React from 'react';
import ReactDOM from 'react-dom';
import { Header } from 'semantic-ui-react';
import { ReportTitle } from './ReportTitle';
import { mount } from 'enzyme';
import * as report from '../api/report';
import { ReadOnlyContext } from '../context/ReadOnly';

jest.mock("../api/report.js")
report.get_changelog = jest.fn().mockReturnValue({ then: jest.fn() });

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<ReportTitle
        report={{ title: "Report" }}
    />, div);
    ReactDOM.unmountComponentAtNode(div);
});

const test_report = {
    report_uuid: "report_uuid"
};

describe("<ReportTitle />", () => {
    it('indicates loading on click', () => {
        report.get_report_pdf = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
        const wrapper = mount(
            <ReadOnlyContext.Provider value={false}>
                <ReportTitle report={test_report} />
            </ReadOnlyContext.Provider>
        );
        wrapper.find(Header).simulate("click");  // Expand title
        wrapper.find("button.left").simulate("click");
        expect(wrapper.find("button.left").hasClass("loading")).toBe(true);
    });
    it('ignores a second click', () => {
        report.get_report_pdf = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
        const wrapper = mount(
            <ReadOnlyContext.Provider value={false}>
                <ReportTitle report={test_report} />
            </ReadOnlyContext.Provider>
        );
        wrapper.find(Header).simulate("click");  // Expand title
        wrapper.find("button.left").simulate("click");
        wrapper.find("button.left").simulate("click");
        expect(wrapper.find("button.left").hasClass("loading")).toBe(true);
    });
    it('loads the pdf', () => {
        report.get_report_pdf = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: (callback => callback()) }) });
        const wrapper = mount(
            <ReadOnlyContext.Provider value={false}>
                <ReportTitle report={test_report} />
            </ReadOnlyContext.Provider>
        );
        wrapper.find(Header).simulate("click");  // Expand title
        wrapper.find("button.left").simulate("click");
        expect(wrapper.find("button.left").hasClass("loading")).toBe(false);
    });
});
