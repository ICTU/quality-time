import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Icon } from 'semantic-ui-react';
import { Button, Popup } from '../semantic_ui_react_wrappers';
import { get_report_pdf } from '../api/report';
import { registeredURLSearchParams } from '../hooks/url_search_query';
import { showMessage } from '../widgets/toast';

function download_pdf(report_uuid, query_string, callback) {
    const reportId = report_uuid ? `report-${report_uuid}` : "reports-overview"
    get_report_pdf(report_uuid, query_string)
        .then(response => {
            if (response.ok === false) {
                showMessage("error", "PDF rendering failed", "HTTP code " + response.status + ": " + response.statusText)
            } else {
                let url = window.URL.createObjectURL(response);
                let a = document.createElement('a');
                a.href = url;
                const now = new Date();
                const local_now = new Date(now.getTime() - (now.getTimezoneOffset() * 60000));
                a.download = `Quality-time-${reportId}-${local_now.toISOString().split(".")[0]}.pdf`;
                a.click();
            }
        }).finally(() => callback());
}

export function DownloadAsPDFButton({ report_uuid }) {
    const [loading, setLoading] = useState(false);
    // Make sure the report_url contains only registered query parameters
    const query = registeredURLSearchParams();
    const queryString = query.toString() ? ("?" + query.toString()) : ""
    query.set("report_url", window.location.origin + window.location.pathname + queryString + window.location.hash);
    const itemType = report_uuid ? "report" : "reports overview"
    const label = `Download ${itemType} as PDF`
    return (
        <Popup
            on={["hover", "focus"]}
            trigger={
                <Button
                    aria-label={label}
                    basic
                    icon
                    loading={loading}
                    onClick={() => {
                        if (!loading) {
                            setLoading(true);
                            download_pdf(report_uuid, `?${query.toString()}`, () => { setLoading(false) })
                        }
                    }}
                    inverted
                >
                    <Icon name="file pdf" /> Download as PDF
                </Button>
            }
            content={`Generate a PDF version of the ${itemType} as currently displayed. This may take some time.`}
        />
    )
}
DownloadAsPDFButton.propTypes = {
    report_uuid: PropTypes.string,
}
