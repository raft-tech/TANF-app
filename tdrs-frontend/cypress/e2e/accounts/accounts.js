/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

When('I log in as a new user', () => {
  cy.login('new-cypress@teamraft.com')
})

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

When('The admin logs in', () => {
  cy.login('new-super-cypress@teamraft.com')
  cy.djangoAdminLogin()
})

Then('I approve a standard user', () => {
  // cy.forceVisit("http://localhost:8080/admin")
  cy.origin('http://localhost:8080/admin', () => {
    cy.visit('/users/user/')
    cy.get(':nth-child(3) > .field-__str__ > a').click()
    cy.get('#id_account_approval_status').select('Approved')
    cy.get('.submit-row > .default').click()
    cy.get('.success').contains('The user “new-cypress@teamraft.com” was changed successfully.').should('exist')
  })
})


When("The admin approves my account", () => {
  cy.adminApproveUser('new-super-cypress@teamraft.com')
})