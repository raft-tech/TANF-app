/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

Then('The user can see the hompage', () => {
  cy.visit('/home')
  cy.contains('You have been approved for access to TDP.').should('exist')
})

When('The user is in begin state', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.reinitUserAccount(`${cypressUser.selector.id}`, `${csrfToken}`)
    })
  })
})

When('The user requests access', () => {
  cy.get('#firstName').type('cypress')
  cy.get('#lastName').type('cypress')
  cy.get('#stt').type('Colorado{enter}')
  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(500).then(() => {
    cy.contains('Request Submitted').should('exist')
  })
})

Then('The user sees request page again', () => {
  cy.visit('/home')
})

Then('The user cannot log in', () => {
  cy.visit('/')
  cy.contains('Inactive Account').should('exist')
})
Then('The user sees the request still submitted', () => {
  cy.visit('/')
  cy.contains('Request Submitted').should('exist')
})