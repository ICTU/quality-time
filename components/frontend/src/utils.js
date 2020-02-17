import React from 'react';
import { toast } from 'react-semantic-toasts';

export function get_metric_name(metric, datamodel) {
    return metric.name || datamodel.metrics[metric.type].name;
}

export function get_source_name(source, datamodel) {
    return source.name || datamodel.sources[source.type].name;
}

export function get_subject_name(subject, datamodel) {
    return subject.name || datamodel.subjects[subject.type].name;
}

export function get_metric_target(metric) {
    return (metric.accept_debt ? metric.debt_target : metric.target) || "0";
}

export function show_message(type, title, description, icon) {
    toast({
      title: title,
      type: type,
      icon: icon,
      size: "large",
      description: <p>{description}</p>,
      time: 30000
    }, () => { }, () => { }, () => { });  // Event handlers are mandatory
  }