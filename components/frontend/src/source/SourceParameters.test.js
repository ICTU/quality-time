import React from 'react';
import ReactDOM from 'react-dom';
import { SourceParameters } from './SourceParameters';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<SourceParameters
        datamodel={{ sources: { source_type: { parameters: { parameter_key: { metrics: [] } } } } }}
        source={{ type: "source_type" }} />, div);
    ReactDOM.unmountComponentAtNode(div);
});