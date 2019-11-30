import React from 'react';
import ReactDOM from 'react-dom';
import { Header } from 'semantic-ui-react';
import { mount } from 'enzyme';
import { ReportTitle } from './ReportTitle';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<ReportTitle
    report={{title: "Report"}}
  />, div);
  ReactDOM.unmountComponentAtNode(div);
});

const report = {
    report_uuid: "report_uuid"
};

describe("<ReportTitle />", () => {
    it('indicates loading on click', () => {
        const wrapper = mount(<ReportTitle report={report} />);
        wrapper.find(Header).simulate("click");  // Expand title
        wrapper.find("button.left").simulate("click");
        expect(wrapper.find("button.left").hasClass("loading")).toBe(true);
    });
});
