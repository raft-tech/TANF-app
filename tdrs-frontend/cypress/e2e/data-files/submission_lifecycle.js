/* eslint-disable no-undef */
import { Before, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import * as df from '../common-steps/data_files.js'

const TEST_DATA_DIR = '../tdrs-backend/tdpservice/parsers/test/data'
const STATUS_TIMEOUT = 90000
const STUCK_TIMEOUT_WAIT = 70000
let longRunningSubmissionId = null
let infectedSubmissionName = null

Before({ tags: '@local-stuck-timeout' }, function () {
  if (!Cypress.env('stuckTimeoutTest')) this.skip()
})

const uploadSectionThroughUI = (
  program,
  year,
  quarter,
  selector,
  file,
  fileName = null
) => {
  cy.intercept('POST', '/v1/data_files/').as('submissionLifecycleUpload')
  df.openDataFilesAndSearch(program, year, quarter)

  const selectedFile = fileName
    ? { contents: `${TEST_DATA_DIR}/${file}`, fileName }
    : `${TEST_DATA_DIR}/${file}`

  cy.get(selector).selectFile(selectedFile, {
    action: 'drag-drop',
    force: true,
    timeout: 60000,
  })
  cy.get('.usa-file-input__preview-image', { timeout: 10000 }).should(
    'not.have.class',
    'is-loading'
  )
  cy.contains('button', 'Submit')
    .should('have.attr', 'data-has-uploaded-files', 'true')
    .click()
  return cy
    .wait('@submissionLifecycleUpload', {
      requestTimeout: 120000,
      responseTimeout: 120000,
    })
    .then(({ response }) => {
      expect(response?.statusCode).to.equal(201)
      expect(response?.body?.id).not.to.equal(undefined)
      return cy
        .get('div.usa-alert--success', { timeout: 60000 })
        .should('be.visible')
        .and('contain.text', 'Successfully uploaded')
        .then(() => response.body)
    })
}

const exactText = (value) => new RegExp(`^${Cypress._.escapeRegExp(value)}$`)

const expectProcessingOrFinished = ($row, fileName, status) => {
  const rowText = $row.text()
  expect(rowText).to.include(fileName)
  expect(rowText).to.match(
    new RegExp(`Pending|${Cypress._.escapeRegExp(status)}`)
  )
}

const latestSectionRowShows = (section, program, fileName, status) => {
  df.getLatestSubmissionHistoryRow(section, program, STATUS_TIMEOUT).should(
    ($row) => expectProcessingOrFinished($row, fileName, status)
  )

  df.getLatestSubmissionHistoryRow(section, program, STATUS_TIMEOUT)
    .contains(exactText(status), { timeout: STATUS_TIMEOUT })
    .should('be.visible')
}

const latestFraRowShows = (fileName, status) => {
  const latestSubmissionRow = () =>
    cy
      .contains('caption', 'Work Outcomes of TANF Exiters Submission History', {
        timeout: STATUS_TIMEOUT,
      })
      .parents('table')
      .find('tbody > tr')
      .first()

  latestSubmissionRow().should(($row) =>
    expectProcessingOrFinished($row, fileName, status)
  )

  latestSubmissionRow()
    .contains(exactText(status), { timeout: STATUS_TIMEOUT })
    .should('be.visible')
}

When(
  'Data Analyst Tim submits a valid TANF aggregate file through the UI',
  () => {
    uploadSectionThroughUI(
      'TANF',
      '2022',
      'Q1',
      '#aggregate_data',
      'ADS.E2J.FTP3.TS06',
      'accepted_tanf_aggregate.txt'
    )
  }
)

Then(
  'Data Analyst Tim sees the TANF aggregate submission finish as Accepted',
  () => {
    latestSectionRowShows(3, 'TANF', 'accepted_tanf_aggregate.txt', 'Accepted')
  }
)

When(
  'Data Analyst Stefani submits an SSP active case file through the UI',
  () => {
    uploadSectionThroughUI(
      'SSP',
      '2024',
      'Q1',
      '#active_case_data',
      'small_ssp_section1.txt'
    )
  }
)

Then(
  'Data Analyst Stefani sees the SSP submission finish as Accepted with Errors',
  () => {
    latestSectionRowShows(
      1,
      'SSP',
      'small_ssp_section1.txt',
      'Accepted with Errors'
    )
  }
)

When('FRA Data Analyst Fred submits an FRA file through the UI', () => {
  cy.visit('/fra-data-files')
  cy.get('h1').contains('FRA Data Files').should('be.visible')
  df.fillFYQ('2024', 'Q2')
  df.uploadFile('#fra-file-upload', `${TEST_DATA_DIR}/fra.csv`)
  cy.contains('button', 'Submit Report').click()
  cy.get('div.usa-alert--success', { timeout: 60000 })
    .should('be.visible')
    .and('contain.text', 'Successfully uploaded')
})

Then(
  'FRA Data Analyst Fred sees the FRA submission finish as Partially Accepted with Errors',
  () => {
    latestFraRowShows('fra.csv', 'Partially Accepted with Errors')
  }
)

When(
  'Data Analyst Tim submits an invalid TANF active case file through the UI',
  () => {
    uploadSectionThroughUI(
      'TANF',
      '2021',
      'Q1',
      '#active_case_data',
      'small_correct_file.txt'
    )
  }
)

Then(
  'Data Analyst Tim sees the TANF active case submission finish as Rejected',
  () => {
    latestSectionRowShows(1, 'TANF', 'small_correct_file.txt', 'Rejected')
  }
)

When('FRA Data Analyst Fred submits an infected file through the UI', () => {
  const eicarTestContent = [
    'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-',
    'ANTIVIRUS-TEST-FILE!$H+H*',
  ].join('')
  infectedSubmissionName = `infected_fra_${Date.now()}.csv`

  cy.visit('/fra-data-files')
  cy.get('h1').contains('FRA Data Files').should('be.visible')
  df.fillFYQ('2024', 'Q2')
  cy.get('#fra-file-upload').selectFile(
    {
      contents: Cypress.Buffer.from(eicarTestContent),
      fileName: infectedSubmissionName,
      mimeType: 'text/csv',
    },
    { action: 'drag-drop', force: true }
  )
  cy.get('.usa-file-input__preview-image', { timeout: 10000 }).should(
    'not.have.class',
    'is-loading'
  )
  cy.contains('button', 'Submit')
    .should('have.attr', 'data-has-uploaded-files', 'true')
    .click()
})

Then(
  'FRA Data Analyst Fred sees that the submission failed security inspection',
  () => {
    cy.get('div.usa-alert--error', { timeout: 60000 })
      .should('be.visible')
      .and(
        'contain.text',
        'Rejected: uploaded file did not pass security inspection'
      )
    cy.contains('Successfully uploaded').should('not.exist')
    cy.contains('caption', 'Work Outcomes of TANF Exiters Submission History')
      .parents('table')
      .should('not.contain.text', infectedSubmissionName)
  }
)

When('Data Analyst Tim submits a long-running TANF file through the UI', () => {
  uploadSectionThroughUI(
    'TANF',
    '2023',
    'Q2',
    '#active_case_data',
    'ADS.E2J.NDM1.TS53_fake.txt',
    'long_running_tanf_active_case.txt'
  ).then((dataFile) => {
    longRunningSubmissionId = dataFile.id
  })
})

Then(
  'Admin Alex eventually sees the submission in Stuck state in the admin UI',
  () => {
    expect(longRunningSubmissionId).not.to.equal(null)
    const adminUrl = new URL(Cypress.env('adminUrl'))
    const adminPath = `${adminUrl.pathname.replace(/\/$/, '')}/data_files/datafile/${longRunningSubmissionId}/change/`

    // CI marks the parse stale after 60 seconds and checks every 5 seconds.
    // Wait before opening the admin page so no reload is needed to observe STUCK.
    cy.wait(STUCK_TIMEOUT_WAIT)

    if (adminUrl.origin === new URL(Cypress.config('baseUrl')).origin) {
      cy.visit(adminPath)
      cy.get('.field-state .readonly', { timeout: 20000 }).should(
        'have.text',
        'Stuck'
      )
      cy.get('.field-parsing_state .readonly').should('have.text', 'Stuck')
      return
    }

    cy.origin(
      adminUrl.origin,
      { args: { adminPath } },
      ({ adminPath: path }) => {
        cy.visit(path)
        cy.get('.field-state .readonly', { timeout: 20000 }).should(
          'have.text',
          'Stuck'
        )
        cy.get('.field-parsing_state .readonly').should('have.text', 'Stuck')
      }
    )
  }
)
