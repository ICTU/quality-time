import React from 'react';
import ReactDOM from 'react-dom';
import { shallow } from 'enzyme';
import { SourceEntityAttribute } from './SourceEntityAttribute';
import { StatusIcon } from '../metric/StatusIcon';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<SourceEntityAttribute entity={{ name: "name" }} entity_attribute={{ key: "name" }} />, div);
    ReactDOM.unmountComponentAtNode(div);
});

describe('<SourceEntityAttribute />', () => {
    it('shows an icon for status', () => {
        const wrapper = shallow(
            <SourceEntityAttribute entity={{ status: "target_met" }} entity_attribute={{ key: "status", type: "status" }} />);
        expect(wrapper.find(StatusIcon).prop("status")).toBe("target_met");
    });
    it('renders an url', () => {
        const wrapper = shallow(
            <SourceEntityAttribute entity={{ status: "target_met", url: "https://url" }} entity_attribute={{ key: "status", type: "status", url: "url" }} />);
        expect(wrapper.find("HyperLink").prop("url")).toBe("https://url");
    });
});