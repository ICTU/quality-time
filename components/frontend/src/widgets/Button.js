import React, { useState } from 'react';
import { Icon, Input } from 'semantic-ui-react';
import { Button, Dropdown, Label, Popup } from '../semantic_ui_react_wrappers';
import { get_report_pdf } from '../api/report';
import { show_message } from '../widgets/toast';
import { decapitalize, registeredURLSearchParams } from '../utils';
import { ItemBreadcrumb } from './ItemBreadcrumb';

function ActionButton(props) {
    const { action, icon, item_type, popup, position, ...other } = props;
    const label = `${action} ${item_type}`;
    const button = <Button basic icon primary {...other} ><Icon name={icon} /> {label}</Button>;
    return (
        popup ?
            <Popup
                content={popup}
                position={position || 'top left'}
                trigger={button}
            /> :
            button
    )
}

export function AddButton({ item_subtypes, item_type, onClick }) {
    const [itemSubType, setItemSubType] = useState(item_subtypes?.[0])
    if (item_subtypes) {
        return (
            <Button.Group>
                <ActionButton
                    action='Add'
                    icon='plus'
                    item_type={`${decapitalize(itemSubType.text)} ${item_type}`}
                    onClick={() => onClick(itemSubType.value)}
                    popup={`Add a new ${decapitalize(itemSubType.text)} ${item_type} here`}
                />
                <Dropdown
                    className="basic button icon primary"
                    onChange={(_event, data) => setItemSubType(item_subtypes.find(t => t.value === data.value))}
                    options={item_subtypes}
                    scrolling
                    style={{ marginRight: "3px" }}
                    trigger={<></>}
                />
            </Button.Group>
        )
    }
    return <ActionButton
        action='Add'
        icon='plus'
        item_type={item_type}
        onClick={() => onClick()}
        popup={`Add a new ${item_type} here`}
    />;
}

export function DeleteButton(props) {
    return (
        <ActionButton
            action='Delete'
            floated='right'
            icon='trash'
            negative
            popup={`Delete this ${props.item_type}. Careful, this can only be undone by a system administrator!`}
            position='top right'
            {...props}
        />
    )
}

function download_pdf(report_uuid, query_string, callback) {
    get_report_pdf(report_uuid, query_string)
        .then(response => {
            if (response.ok === false) {
                show_message("error", "PDF rendering failed", "HTTP code " + response.status + ": " + response.statusText)
            } else {
                let url = window.URL.createObjectURL(response);
                let a = document.createElement('a');
                a.href = url;
                const now = new Date();
                const local_now = new Date(now.getTime() - (now.getTimezoneOffset() * 60000));
                a.download = `Quality-time-report-${report_uuid}-${local_now.toISOString().split(".")[0]}.pdf`;
                a.click();
            }
        }).finally(() => callback());
}

export function DownloadAsPDFButton(props) {
    const [loading, setLoading] = useState(false);
    const { report_uuid, history, ...otherProps } = props;
    // Make sure the report_url contains only registered query parameters
    const query = registeredURLSearchParams(history);
    const queryString = query.toString() ? ("?" + query.toString()) : ""
    query.set("report_url", window.location.origin + window.location.pathname + queryString + window.location.hash);
    return (
        <ActionButton
            action='Download'
            icon="file pdf"
            item_type='report as pdf'
            loading={loading}
            onClick={() => {
                if (!loading) {
                    setLoading(true);
                    download_pdf(report_uuid, `?${query.toString()}`, () => { setLoading(false) })
                }
            }}
            {...otherProps}
        />
    )
}

function ReorderButton(props) {
    const label = `Move ${props.moveable} to the ${props.direction} ${props.slot || 'position'}`;
    const icon = { "first": "double up", "last": "double down", "previous": "up", "next": "down" }[props.direction];
    const disabled = (props.first && (props.direction === "first" || props.direction === "previous")) ||
        (props.last && (props.direction === "last" || props.direction === "next"));
    return (
        <Popup content={label} trigger={
            <Button
                aria-label={label}
                basic
                disabled={disabled}
                icon={`angle ${icon}`}
                onClick={() => props.onClick(props.direction)}
                primary
            />}
        />
    )
}

export function ReorderButtonGroup(props) {
    return (
        <Button.Group style={{ marginTop: "0px" }}>
            <ReorderButton {...props} direction="first" />
            <ReorderButton {...props} direction="previous" />
            <ReorderButton {...props} direction="next" />
            <ReorderButton {...props} direction="last" />
        </Button.Group>
    )
}

function ActionAndItemPickerButton({ action, item_type, onChange, get_options, icon }) {
    const [options, setOptions] = useState([]);

    var breadcrumb_props = { report: "report" };
    if (item_type !== 'report') {
        breadcrumb_props.subject = 'subject';
        if (item_type !== 'subject') {
            breadcrumb_props.metric = 'metric';
            if (item_type !== 'metric') {
                breadcrumb_props.source = 'source';
            }
        }
    }
    return (
        <Popup
            content={`${action} an existing ${item_type} here`}
            trigger={
                <Dropdown
                    basic
                    className='button icon primary'
                    floating
                    header={<Dropdown.Header><ItemBreadcrumb size='tiny' {...breadcrumb_props} /></Dropdown.Header>}
                    options={options}
                    onChange={(_event, { value }) => onChange(value)}
                    onOpen={() => setOptions(get_options())}
                    scrolling
                    selectOnBlur={false}
                    selectOnNavigation={false}
                    trigger={<><Icon name={icon} /> {`${action} ${item_type} `}</>}
                    value={null}  // Without this, a selected item becomes active (shown bold in the menu) and can't be selected again
                />}
        />
    )
}

export function CopyButton(props) {
    return (
        <ActionAndItemPickerButton {...props} action="Copy" icon="copy" />
    )
}

export function MoveButton(props) {
    return (
        <ActionAndItemPickerButton {...props} action="Move" icon="shuffle" />
    )
}

export function PermLinkButton({ url }) {
    if (navigator.clipboard) {
        // Frontend runs in a secure context (https) so we can use the Clipboard API
        return (
            <Button
                as="div"
                labelPosition="right"
                onClick={() => navigator.clipboard.writeText(url).then(function () {
                    show_message("success", 'Copied URL to clipboard')
                }, function () {
                    show_message("error", 'Failed to copy URL to clipboard')
                })}
            >
                <Button
                    basic
                    content='Copy'
                    icon='copy'
                    primary
                />
                <Label as="a" color="blue">{url}</Label>
            </Button>
        )
    } else {
        // Frontend does not run in a secure context (https) so we cannot use the Clipboard API, and have
        // to use the deprecated Document.execCommand. As document.exeCommand expects selected text, we also
        // cannot use the Label component but have to use a (read only) input element so we can select the URL
        // before copying it to the clipboard.
        return (
            <Input
                action
                actionPosition='left'
                color="blue"
                defaultValue={url}
                fluid
                readOnly
            >
                <Button
                    basic
                    color="blue"
                    content="Copy"
                    icon="copy"
                    onClick={() => {
                        let urlText = document.querySelector("#permlink")
                        urlText.select()
                        document.execCommand("copy")
                        show_message("success", 'Copied URL to clipboard')
                    }}
                    style={{ fontWeight: "bold" }}
                />
                <input id="permlink" style={{ border: "1px solid rgb(143, 208, 255)", color: "rgb(143, 208, 255)", fontWeight: "bold" }} />
            </Input>
        )
    }
}