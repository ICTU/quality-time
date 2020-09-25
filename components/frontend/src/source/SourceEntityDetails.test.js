import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import * as source from '../api/source';
import { SourceEntityDetails } from './SourceEntityDetails';

jest.mock("../api/source.js")

const data_model = {
    sources: {
        pip: {
            entities: {
                dependencies: {
                    statuses: {
                        unconfirmed: {
                            name: "Unconfirmed"
                        },
                        confirmed: {
                            name: "Confirmed"
                        },
                        ignored: {
                            name: "Ignored"
                        }
                    }
                }
            }
        }
    }
};

function source_entity_details(source_type = 'sonarqube', metric_type = 'violations', entity_type = 'violation') {
    return mount(
        <ReadOnlyContext.Provider value={false}>
            <SourceEntityDetails
                data_model={data_model} entity={{ key: "key" }} status="unconfirmed" name={entity_type}
                metric_type={metric_type} source_type={source_type} />
        </ReadOnlyContext.Provider>
    )
}

describe('<SourceEntityDetails />', () => {
    beforeEach(() => { source.set_source_entity_attribute = jest.fn(); });
    it('invokes the callback on changing the status', () => {
        const wrapper = source_entity_details();
        wrapper.find("div.item").at(0).simulate("click");
        expect(source.set_source_entity_attribute).toHaveBeenCalled();
    });
    it('invokes the callback on changing the comment', () => {
        const wrapper = source_entity_details();
        wrapper.find("textarea").at(0).simulate("change", { target: { value: "comment" } });
        wrapper.find("TextInput").at(0).simulate("submit");
        expect(source.set_source_entity_attribute).toHaveBeenCalled();
    });
    it('lists the default statuses', () => {
        const wrapper = source_entity_details();
        const options = wrapper.find("SingleChoiceInput").prop("options");
        const keys = options.map(option => option.key)
        expect(keys).toStrictEqual(["confirmed", "false_positive", "fixed", "unconfirmed", "wont_fix"]);
    });
    it('uses non-default statuses if present in the data model', () => {
        const wrapper = source_entity_details("pip", "dependencies", "dependency");
        const options = wrapper.find("SingleChoiceInput").prop("options");
        const keys = options.map(option => option.key)
        expect(keys.sort()).toStrictEqual(["confirmed", "ignored", "unconfirmed"]);
    });
});