import { ItemBreadcrumb } from "./ItemBreadcrumb"
import { metricOptions, reportOptions, sourceOptions, subjectOptions } from "./menu_options"

it("contains the reports", () => {
    expect(
        reportOptions([
            { report_uuid: "report1", title: "B" },
            { report_uuid: "report2", title: "A" },
        ]),
    ).toStrictEqual([
        { content: "A", key: "report2", text: "A", value: "report2" },
        { content: "B", key: "report1", text: "B", value: "report1" },
    ])
})

it("contains the subjects, except for the excluded report", () => {
    expect(
        subjectOptions(
            [
                { report_uuid: "report1", title: "B" },
                { report_uuid: "report2", title: "A", subjects: { subject1: { name: "S" } } },
            ],
            {},
            "report1",
        ),
    ).toStrictEqual([
        {
            key: "subject1",
            text: "AS",
            value: "subject1",
            content: <ItemBreadcrumb report="A" subject="S" />,
        },
    ])
})

it("contains the metrics, except for the excluded subject", () => {
    expect(
        metricOptions(
            [
                {
                    report_uuid: "report1",
                    title: "B",
                    subjects: { subject2: { name: "S2", type: "subject_type" } },
                },
                {
                    report_uuid: "report2",
                    title: "A",
                    subjects: {
                        subject1: {
                            name: "S1",
                            type: "subject_type",
                            metrics: {
                                metric1: { name: "M1", type: "metric_type" },
                                metric2: { name: "M2", type: "other_metric_type" },
                            },
                        },
                    },
                },
            ],
            { subjects: { subject_type: { metrics: ["metric_type"] } } },
            "subject_type",
            "subject2",
        ),
    ).toStrictEqual([
        {
            key: "metric1",
            text: "AS1M1",
            value: "metric1",
            content: <ItemBreadcrumb report="A" subject="S1" metric="M1" />,
        },
    ])
})

it("contains the sources, except for the excluded metric", () => {
    expect(
        sourceOptions(
            [
                {
                    report_uuid: "report1",
                    title: "B",
                    subjects: { subject2: { name: "S2", type: "subject_type", metrics: [] } },
                },
                {
                    report_uuid: "report2",
                    title: "A",
                    subjects: {
                        subject1: {
                            name: "S1",
                            type: "subject_type",
                            metrics: {
                                metric1: { name: "M1", type: "metric_type", sources: [] },
                                metric2: {
                                    name: "M2",
                                    type: "metric_type",
                                    sources: {
                                        source1: { name: "S1", type: "source_type" },
                                        source2: { name: "S2", type: "other_source_type" },
                                    },
                                },
                            },
                        },
                    },
                },
            ],
            { metrics: { metric_type: { sources: ["source_type"] } } },
            "metric_type",
            "metric1",
        ),
    ).toStrictEqual([
        {
            key: "source1",
            text: "AS1M2S1",
            value: "source1",
            content: <ItemBreadcrumb report="A" subject="S1" metric="M2" source="S1" />,
        },
    ])
})
