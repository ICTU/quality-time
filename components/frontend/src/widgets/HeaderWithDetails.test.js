import React from 'react';
import ReactDOM from 'react-dom';
import { Icon, Header } from 'semantic-ui-react';
import { shallow } from 'enzyme';
import { HeaderWithDetails } from './HeaderWithDetails';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<HeaderWithDetails />, div);
    ReactDOM.unmountComponentAtNode(div);
});

describe('<HeaderWithDetails />', () => {
    it('changes the caret on mouse click', () => {
        const wrapper = shallow(<HeaderWithDetails />);
        expect(wrapper.find(Icon).prop("name")).toBe("caret right");
        wrapper.find(Header).simulate("click");
        expect(wrapper.find(Icon).prop("name")).toBe("caret down");
    });

    it('changes the caret on key press', () => {
        const wrapper = shallow(<HeaderWithDetails />);
        expect(wrapper.find(Icon).prop("name")).toBe("caret right");
        wrapper.find(Header).simulate("keyPress");
        expect(wrapper.find(Icon).prop("name")).toBe("caret down");
    })
});