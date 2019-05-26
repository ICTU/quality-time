import {Given, When, Then} from "cypress-cucumber-preprocessor/steps";


Given(/^a metric whose measurement value is (.+) as the target value$/, (startValue) => {
    cy.get("#root > div > div.ui.fluid.container > div > table > tbody > tr:nth-child(3)")
        .as('testLineCoverage');

    cy.get("@testLineCoverage").within(() => {
        cy.get('td:nth-child(4) > i')
        .should('have.class', startValue);
    });
    cy.get("#root > div > div.ui.fluid.container > div > table > tbody > tr:nth-child(4)")
        .as('metricScreen');

    cy.get("@metricScreen").within(() => {
        cy.get('.tabbutton').contains('Metric').click();
    });
});

When(/^the quality manager changes debt target to (.+), Metric target to (.+) and Accept technical debt to (.+)$/, (debtChanged, metricChanged, acceptTdChanged) => {

    cy.get("@metricScreen").within(() => {
        cy.get('td > div > div.ui.bottom.attached.segment.active.tab > div.ui.stackable.grid > div:nth-child(3)')
            .as('innerMetricScreen');
        cy.get('td > div > div.ui.bottom.attached.segment.active.tab > div.ui.stackable.grid > div:nth-child(2)').within(() => {
            cy.get('div:nth-child(1) > form > div > div').within( () => {
                cy.get('div > input[type=number]')
                    .clear()
                    .type(metricChanged);
            })
        })
    });

    cy.get('@innerMetricScreen').within( () => {
        cy.get('div:nth-child(2) > form > div > div').within( () => {
            cy.get('div > input[type=number]')
                .clear()
                .type(debtChanged);
        });
        cy.get('div:nth-child(1) > form > div > div').within(() => {
            cy.get('> i').click();
            cy.get(`div.visible.menu.transition > div:nth-child(${acceptTdChanged})`).click();
        });
    });
});

Then(/^the metric is marked as (.+)$/, (endTarget) => {
    cy.get("@testLineCoverage").within(() => {
        cy.get('td:nth-child(4) > i')
            .should('have.class', endTarget);
    });
});
