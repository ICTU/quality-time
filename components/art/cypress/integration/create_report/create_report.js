import { When, Then } from "cypress-cucumber-preprocessor/steps";

When(/^the quality manager creates a new report$/, () => {
    cy.contains('button', 'Add report').click();
    cy.contains('a.ui.card', 'New report').click();
});

When(/^the quality manager adds a new subject$/, () => {
    cy.wait(2000);
    cy.contains('button', 'Add subject').click();
});

When(/^the quality manager adds a new metric$/, () => {
    cy.wait(2000);
    cy.contains('button', 'Add metric').click();
});

When(/^the quality manager sets the metric target value to (.+)$/, (metric_target_value) => {
    cy.get('input[type=number]').first().type("{selectall}").type(metric_target_value).blur();
});

Then(/^the metric target is (.+)$/, (expected_metric_target_value) => {
    cy.wait(2000);
    cy.get("table.ui.sortable.table > tbody > tr:first-child > td:nth-child(6)").should('contain',
        expected_metric_target_value);
});
