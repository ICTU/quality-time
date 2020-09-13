export function entity_status(data_model) {
    return Object.fromEntries(Object.entries(data_model.entities.statuses).filter(([_, status]) => status.default));
}