import React from 'react';
import { ItemBreadcrumb } from './widgets/ItemBreadcrumb';
import { get_subject_name } from './utils';

export function subject_options(reports, datamodel, current_subject_uuid) {
    let options = [];
    reports.forEach((report) => {
      Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const subject_name = get_subject_name(subject, datamodel);
        options.push({
          content: <ItemBreadcrumb report={report.title} subject={subject_name} />,
          disabled: subject_uuid === current_subject_uuid, key: subject_uuid,
          text: report.title + subject_name,
          value: subject_uuid
        })
      })
    });
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
  }
