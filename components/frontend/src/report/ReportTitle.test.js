import React from 'react';
import ReactDOM from 'react-dom';
import { ReportTitle } from './ReportTitle';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<ReportTitle
        report={{ title: "Report" }}
    />, div);
    ReactDOM.unmountComponentAtNode(div);
});
