import {Given, When, Then} from "cypress-cucumber-preprocessor/steps";


Given(/^a metric whose measurement value is (.+) as the target value$/, (startValue) => {
    cy.get("table.ui.sortable.table > tbody > tr:nth-child(4)")
        .as('testLineCoverage');

    cy.get("@testLineCoverage").within(() => {
        cy.get('td:nth-child(4) > i')
        .should('have.class', startValue);
    });
    cy.get("table.ui.sortable.table > tbody > tr:nth-child(5)")
        .as('metricDetails');

    cy.get("@metricDetails").within(() => {
        cy.get('.tabbutton').contains('Metric').click();
    });
});

When(/^the quality manager changes debt target to (.+), Metric target to (.+) and Accept technical debt to (.+)$/, (debtChanged, metricChanged, acceptTdChanged) => {

    cy.get("@metricDetails").within(() => {
        cy.get('> td > div > div.ui.bottom.attached.segment.active.tab > div.ui.stackable.grid > div:nth-child(3)')
            .as('metricDebt');
        cy.get('td > div > div.ui.bottom.attached.segment.active.tab > div.ui.stackable.grid > div:nth-child(2)').within(() => {
            cy.get('div:nth-child(1) > form > div > div').within( () => {
                cy.get('div > input[type=number]')
                    .clear()
                    .type(metricChanged);
            })
        })
    });

    cy.get('@metricDebt').within( () => {
        cy.get('> div:nth-child(2) > form > div > div').within( () => {
            cy.get('div > input[type=number]')
                .clear()
                .type(debtChanged);
        });
        cy.wait(2000);
        cy.get('> div:nth-child(1) > form > div > div').within(() => {
            cy.get('> i').click();
            cy.get(`div.visible.menu.transition > div:nth-child(${acceptTdChanged})`).click();
        });
    });
});

Then(/^the metric is marked as (.+)$/, (endTarget) => {
    cy.wait(2000);
    cy.get("@testLineCoverage").within(() => {
        cy.get('> td:nth-child(4) > i')
            .should('have.class', endTarget);
    });
});
