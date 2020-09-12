export const source_entity_status_name = {
    unconfirmed: "Unconfirmed",
    confirmed: "Confirmed",
    fixed: "Fixed",
    false_positive: "False positive",
    wont_fix: "Won't fix"
}

export function entity_status(data_model, entity_type = 'default') {
    return data_model.entities[entity_type].status;
}