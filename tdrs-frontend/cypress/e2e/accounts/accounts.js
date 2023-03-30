/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('I see a Request Access form', () => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

When('The admin approves the user', () => {
  cy.get('@cypressUser').then((cypressUser) => {
    cy.get('@adminCsrfToken').then((csrfToken) => {
      cy.approveUser(`${cypressUser.selector.id}`, `${csrfToken}`)
    })
  })
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
  cy.get('#firstName').type(Cypress.env('cypressName'))
  cy.get('#lastName').type(Cypress.env('cypressName'))
  cy.get('#stt').type(Cypress.env('cypressSttName')).type('{enter}')
  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(300).then(() => {
    cy.contains('Request Submitted').should('exist')
  })
})
