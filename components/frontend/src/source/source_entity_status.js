export function source_entity_statuses(entity_type) {
    return {
        unconfirmed: {
            name: "Unconfirmed",
            action: "Unconfirm",
            description: `This ${entity_type} should be reviewed to decide what to do with it.`,
            ignored: false
        },
        confirmed: {
            name: "Confirmed",
            action: "Confirm",
            description: `This ${entity_type} has been reviewed and should be dealt with.`,
            ignored: false
        },
        fixed: {
            name: "Fixed",
            action: "Resolve as fixed",
            description: `This ${entity_type} has been fixed and will disappear shortly.`,
            ignored: true
        },
        false_positive: {
            name: "False positive",
            action: "Resolve as false positive",
            description: `This ${entity_type} can be ignored because it's been incorrectly identified as ${entity_type}.`,
            ignored: true
        },
        wont_fix: {
            name: "Won't fix",
            action: "Resolve as won't fix",
            description: `This ${entity_type} will not be fixed.`,
            ignored: true
        }
    }
}
