import React from 'react';
import ReactDOM from 'react-dom';
import { DataModel } from '../context/DataModel';
import { SourceParameters } from './SourceParameters';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(
        <DataModel.Provider  value={{ sources: { source_type: { parameters: { parameter_key: { metrics: [] } } } } }}>
            <SourceParameters
                source={{ type: "source_type" }} />
        </DataModel.Provider>, div);
    ReactDOM.unmountComponentAtNode(div);
});