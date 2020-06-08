import React from 'react';
import { ItemBreadcrumb } from './widgets/ItemBreadcrumb';
import { get_metric_name, get_source_name, get_subject_name } from './utils';

export function metric_options(reports, datamodel, current_subject_uuid) {
    let options = [];
    reports.forEach((report) => {
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            if (subject_uuid === current_subject_uuid) { return }
            const subject_name = get_subject_name(subject, datamodel);
            Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                const metric_name = get_metric_name(metric, datamodel);
                options.push({
                    content: <ItemBreadcrumb report={report.title} subject={subject_name} metric={metric_name} />,
                    key: metric_uuid,
                    text: report.title + subject_name + metric_name,
                    value: metric_uuid
                })
            })
        });
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function report_options(reports, current_report_uuid) {
    let options = [];
    reports.forEach((report) => {
        options.push({
            disabled: report.report_uuid === current_report_uuid, key: report.report_uuid,
            text: report.title, value: report.report_uuid
        })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function source_options(reports, datamodel, current_metric_uuid) {
    let options = [];
    reports.forEach((report) => {
        Object.values(report.subjects).forEach((subject) => {
            const subject_name = get_subject_name(subject, datamodel);
            Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                if (metric_uuid === current_metric_uuid) { return }
                const metric_name = get_metric_name(metric, datamodel);
                Object.entries(metric.sources).forEach(([source_uuid, source]) => {
                    const source_name = get_source_name(source, datamodel);
                    options.push({
                        content: <ItemBreadcrumb report={report.title} subject={subject_name} metric={metric_name} source={source_name} />,
                        key: source_uuid,
                        text: report.title + subject_name + metric_name + source_name,
                        value: source_uuid
                    })
                })
            })
        })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
}

export function subject_options(reports, datamodel, current_report_uuid) {
    let options = [];
    reports.forEach((report) => {
      if (report.report_uuid === current_report_uuid) { return }
      Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const subject_name = get_subject_name(subject, datamodel);
        options.push({
          content: <ItemBreadcrumb report={report.title} subject={subject_name} />,
          key: subject_uuid,
          text: report.title + subject_name,
          value: subject_uuid
        })
      })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
  }
