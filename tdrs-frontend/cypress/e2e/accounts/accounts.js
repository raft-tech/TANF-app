/* eslint-disable no-undef */
import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

Then('{string} sees a Request Access form', (username) => {
  cy.contains('Welcome').should('exist')
  cy.get('button').contains('Request Access').should('exist')
})

Then('{string} can see the hompage', (username) => {
  cy.visit('/home')
  cy.contains('You have been approved for access to TDP.').should('exist')
})

When('{string} is in begin state', (username) => {
  cy.get('@cypressUser').then((cypressUser) => {
    let body = {
      username: username,
      first_name: '',
      last_name: '',
      email: username,
      stt: '',
      region: '',
      account_approval_status: 'Initial',
      access_requested_date_0: '0001-01-01',
      access_requested_date_1: '00:00:00',
      _save: 'Save',
    }


    cy.adminApiRequest(
      'POST',
      `/users/user/${cypressUser.selector.id}/change/`,
      body
    )
  })
})

When('{string} requests access', (username) => {
  cy.get('#firstName').type('cypress')
  cy.get('#lastName').type('cypress')
  cy.get('#stt').type('Colorado{enter}')
  cy.get('button').contains('Request Access').should('exist').click()
  cy.wait(2000).then(() => {
    cy.contains('Request Submitted').should('exist')
  })
})

Then('{string} sees request page again', (username) => {
  cy.visit('/home')
})

Then('{string} cannot log in', (username) => {
  cy.visit('/')
  cy.contains('Inactive Account').should('exist')
})
Then('{string} sees the request still submitted', (username) => {
  cy.visit('/')
  cy.contains('Request Submitted').should('exist')
})

Then('{string} can see Data Files page', (username) => {
  cy.visit('/data-files')
  cy.contains('Data Files').should('exist')
})

Then('{string} can see search form', (username) => {
  cy.contains('Fiscal Year').should('exist')
  cy.contains('Quarter').should('exist')
})

Then('{string} can browse upload file form', (username) => {
  cy.get('#reportingYears').should('exist').select('2023')
  cy.get('#quarter').should('exist').select('Q1')
  cy.get('button').contains('Search').should('exist')
})

When('{string} uploads a file', (username) => {
  cy.get('button').contains('Search').should('exist').click()
  cy.get('#closed-case-data').selectFile('../tdrs-backend/tdpservice/parsers/test/data/small_correct_file',{ action: 'drag-drop' })
  cy.get('button').contains('Submit Data Files').should('exist').click()

})

Then('{string} can see the upload successful', (username) => {
  cy.wait(3000).then(() => {
    const runout = ['No changes have been made to data files', 'Sucessfully']
    cy.contains(/Successfully|No changes/g).should('exist')
    //const regex = new RegExp(`${runout.join('|')}`, 'g')
    //cy.get('p').should('have.class','usa-alert__text').should('exist').contains('No changes have been made to data files')
  })
})
