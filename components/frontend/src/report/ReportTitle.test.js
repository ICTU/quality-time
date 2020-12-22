import React from 'react';
import ReactDOM from 'react-dom';
import { ReportTitle } from './ReportTitle';

let mockHistory = {location: {}};

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<ReportTitle
        history={mockHistory}
        report={{ title: "Report" }}
    />, div);
    ReactDOM.unmountComponentAtNode(div);
});
