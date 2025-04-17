import { TableBody } from "@mui/material"
import { array, func, string } from "prop-types"
import React, { useEffect, useRef, useState } from "react"

import {
    datesPropType,
    measurementsPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { SubjectTableRow } from "./SubjectTableRow"
import { set_metric_attribute } from "../api/metric"

function copyAllComputedStyles(sourceNode, targetNode) {
    const sourceStyles = getComputedStyle(sourceNode);
    for (const key of sourceStyles) {
        try {
            targetNode.style[key] = sourceStyles.getPropertyValue(key);
        } catch {}
    }

    // Recursively copy to children
    const sourceChildren = Array.from(sourceNode.children);
    const targetChildren = Array.from(targetNode.children);
    for (let i = 0; i < sourceChildren.length; i++) {
        copyAllComputedStyles(sourceChildren[i], targetChildren[i]);
    }
}

export function SubjectTableBody({
    changedFields,
    columnsToHide,
    dates,
    handleSort,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    reversedMeasurements,
    settings,
    subjectUuid,
}) {
    const [dragOverIndex, setDragOverIndex] = useState(null);

    const dragItem = useRef(null);
    const dragOverItem = useRef(null);

    const handleDragStart = (index, rowRef, event) => {
        dragItem.current = index;
        event.dataTransfer.effectAllowed = "move";

        if (rowRef?.current) {
            const clonedRow = rowRef.current.cloneNode(true);

            copyAllComputedStyles(rowRef.current, clonedRow);

            const wrapper = document.createElement("table");
            const tbody = document.createElement("tbody");

            wrapper.appendChild(tbody);
            tbody.appendChild(clonedRow);

            wrapper.style.position = "absolute";
            wrapper.style.borderCollapse = "collapse";
            wrapper.style.tableLayout = "auto"
            wrapper.style.width = `${rowRef.current.offsetWidth}px`;

            document.body.appendChild(wrapper);

            const rowRect = rowRef.current.getBoundingClientRect();
            const offsetX = event.clientX - rowRect.left;
            const offsetY = event.clientY - rowRect.top;

            // Shift the ghost slightly left of the cursor, but not out of bounds
            const adjustedOffsetX = Math.max(0, offsetX);

            event.dataTransfer.setDragImage(wrapper, adjustedOffsetX, offsetY);

            setTimeout(() => {
                document.body.removeChild(wrapper);
            }, 0);
        }
    };

    const handleDragEnter = (index) => {
        setDragOverIndex(index);
        dragOverItem.current = index;
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const dragFrom = dragItem.current;
        const dropTarget = dragOverItem.current;

        if (dragFrom == null || dropTarget == null || dragFrom === dropTarget) return;

        const [movedUUID] = metricEntries[dragFrom];

        dragItem.current = null;
        dragOverItem.current = null;
        setDragOverIndex(null);

        // Persist to backend and reload
        set_metric_attribute(movedUUID, "position_index", dropTarget, reload);
    };

    useEffect(() => {
        const handleDragEnd = () => {
            dragItem.current = null;
            dragOverItem.current = null;
            setDragOverIndex(null);
        };

        window.addEventListener("dragend", handleDragEnd);
        return () => {
            window.removeEventListener("dragend", handleDragEnd);
        };
    }, []);

    const lastIndex = metricEntries.length - 1;

    return (
        <TableBody>
            {metricEntries.map(([metricUuid, metric], index) => (
                <React.Fragment key={metric_uuid}>
                    {dragOverIndex === index && (
                        <tr style={{ height: '4px' }}>
                            <td colSpan="100%">
                                <div
                                    style={{
                                        height: '4px',
                                        backgroundColor: '#1976d2',
                                        boxShadow: '0 0 3px rgba(25, 118, 210, 0.8)',
                                        borderRadius: '2px',
                                        margin: '2px 0',
                                    }}
                                />
                            </td>
                        </tr>
                    )}
                    <SubjectTableRow
                        changedFields={changedFields}
                        dates={dates}
                        columnsToHide={columnsToHide}
                        handleSort={handleSort}
                        index={index}
                        key={metricUuid}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metricUuid={metricUuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subjectUuid={subjectUuid}
                        onDragStart={handleDragStart}
                        onDragEnter={handleDragEnter}
                        onDrop={(e) => handleDrop(e)}
                        isDropTarget={dragOverIndex === index}
                    />
                </React.Fragment>
            ))}
        </TableBody>
    )
}
SubjectTableBody.propTypes = {
    changedFields: stringsPropType,
    columnsToHide: stringsPropType,
    dates: datesPropType,
    handleSort: func,
    measurements: measurementsPropType,
    metricEntries: array,
    reload: func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: measurementsPropType,
    settings: settingsPropType,
    subjectUuid: string,
}
