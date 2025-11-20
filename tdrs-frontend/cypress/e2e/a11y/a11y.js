/// <reference types="cypress" />

import { ACTORS, clearCookies } from '../common-steps/common-steps'

function terminalLog(violations) {
  cy.task(
    'log',
    `${violations.length} accessibility violation${
      violations.length === 1 ? '' : 's'
    } ${violations.length === 1 ? 'was' : 'were'} detected`
  )

  const violationData = violations.map(
    ({ id, impact, description, nodes }) => ({
      id,
      impact,
      description,
      nodes: nodes.length,
    })
  )

  cy.task('table', violationData)
}

/**
 * Helper: log in once as a known user.
 * This is essentially what the Cucumber step `{string} logs in` does,
 * but hard-coded to "Data Analyst Tim".
 */
const loginAsDataAnalystStefani = () => {
  clearCookies()

  // Prepare admin context (like the Given step does),
  // so account status is in a good state if needed.
  cy.visit('/')
  cy.adminLogin('cypress-admin-alex@teamraft.com')

  cy.contains('Sign into TANF Data Portal', { timeout: 30000 })

  // Now log in as a portal user
  const username = ACTORS['Data Analyst Stefani'].username
  cy.login(username)
}

/* ───────────── PUBLIC PAGES ───────────── */

describe('Public pages accessibility', () => {
  const publicPages = [
    { name: 'Landing', path: '/' },
    { name: 'Login', path: '/login' },
  ]

  publicPages.forEach((page) => {
    it(`has no serious accessibility violations on ${page.name}`, () => {
      cy.visit(page.path)
      cy.injectAxe()

      cy.checkA11y(
        null,
        {
          includedImpacts: ['critical', 'serious'],
        },
        terminalLog
      )
    })
  })
})

/* ───────────── AUTHENTICATED PAGES ───────────── */

describe('Authenticated pages accessibility', () => {
  const authedPages = [
    { name: 'Home', path: '/home' },
    { name: 'Data files', path: '/data-files' },
    // add profile or others here if you like:
    { name: 'Profile', path: '/profile' },
  ]

  // Log in ONCE for this suite
  before(() => {
    loginAsDataAnalystStefani()
  })

  authedPages.forEach((page) => {
    it(`has no serious accessibility violations on ${page.name}`, () => {
      cy.visit(page.path)
      cy.injectAxe()

      cy.checkA11y(
        null,
        {
          includedImpacts: ['critical', 'serious'],
        },
        terminalLog
      )
    })
  })
})