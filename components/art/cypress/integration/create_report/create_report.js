import { When, Then } from "cypress-cucumber-preprocessor/steps";

function waitForBrowser() {
    cy.window().then(win => {
        return new Cypress.Promise(resolve => win['requestIdleCallback'](resolve));
    });
}

When(/^the quality manager creates a new report$/, () => {
    cy.contains('button', 'Add report').click();
    waitForBrowser();
    cy.get('a.ui.card').contains("New report").click();
});

When(/^the quality manager adds a new subject$/, () => {
    waitForBrowser();
    cy.contains('.button', 'Add subject', {}).click();
});

When(/^the quality manager adds a new metric$/, () => {
    waitForBrowser();
    cy.contains('.button', 'Add metric').click();
});

When(/^the quality manager sets the metric target value to (.+)$/, (metric_target_value) => {
    waitForBrowser();
    cy.get('input[type=number]').first().type("{selectall}").type(metric_target_value).blur();
});

Then(/^the metric target is (.+)$/, (expected_metric_target_value) => {
    waitForBrowser();
    cy.get("table.ui.sortable.table > tbody > tr:first-child > td:nth-child(6)").should('contain',
        expected_metric_target_value);
});
