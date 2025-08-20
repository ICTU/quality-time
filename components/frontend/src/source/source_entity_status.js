import { entityPropType, sourcePropType } from "../sharedPropTypes"

export const IGNORABLE_SOURCE_ENTITY_STATUSES = ["false_positive", "fixed", "wont_fix"]

export const SOURCE_ENTITY_STATUS_NAME = {
    unconfirmed: "Unconfirmed",
    confirmed: "Confirmed",
    fixed: "Fixed",
    false_positive: "False positive",
    wont_fix: "Won't fix",
}

export const SOURCE_ENTITY_STATUS_ACTION = {
    unconfirmed: "Unconfirm",
    confirmed: "Confirm",
    fixed: "Mark as fixed",
    false_positive: "Mark as false positive",
    wont_fix: "Mark as won't fix",
}

export const SOURCE_ENTITY_STATUS_DESCRIPTION = {
    // Unconfirmed is missing because these descriptions are only used for the desired response times at the moment
    confirmed: "Confirmed means that an entity has been reviewed and should be dealt with.",
    fixed: "Fixed means that an entity can be ignored because it has been fixed, or will be fixed shortly, and thus disappear.",
    false_positive:
        "False positive means an entity has been incorrectly identified as a problem and should be ignored.",
    wont_fix: "Won't fix means that an entity can be ignored because it will not be fixed.",
}

export function entityStatus(source, entity) {
    return source.entity_user_data?.[entity.key]?.status ?? "unconfirmed"
}
entityStatus.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}

export function entityStatusEndDate(source, entity) {
    return source.entity_user_data?.[entity.key]?.status_end_date ?? ""
}
entityStatusEndDate.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}

export function entityStatusRationale(source, entity) {
    return source.entity_user_data?.[entity.key]?.rationale ?? ""
}
entityStatusRationale.propTypes = {
    source: sourcePropType,
    entity: entityPropType,
}
