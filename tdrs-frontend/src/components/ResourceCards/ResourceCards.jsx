import Button from '../Button'

function ResourceCards() {
  return (
    <section className="padding-top-4 usa-section">
      <div className="grid-row">
        <div className="mobile:grid-container desktop:padding-0 desktop:grid-col-3">
          <h2 className="resources-header font-heading-2xl margin-top-0 margin-bottom-0">
            Featured TANF Resources
          </h2>
          <div>
            <p>Questions about TANF data?</p>
            <p>
              Email:{' '}
              <a className="usa-link" href="mailto: tanfdata@acf.hhs.gov">
                tanfdata@acf.hhs.gov
              </a>
            </p>
          </div>
        </div>
        <div className="desktop:grid-col-9">
          <ul className="grid-row usa-card-group mobile:margin-0">
            <li className="usa-card--header-first padding-bottom-4 desktop:padding-right-2 desktop:grid-col-6 mobile:grid-col-12">
              <div className="usa-card__container">
                <header className="usa-card__header">
                  <h3 className="usa-card__heading">TDP Knowledge Center</h3>
                </header>
                <div className="usa-card__body">
                  <p>
                    The knowledge center contains resources on all things TDP
                    from account creation to data submission.
                  </p>
                </div>
                <div className="usa-card__footer">
                  <Button
                    type="button"
                    class="usa-button"
                    id="viewKnowledgeCenterButton"
                    href="http://tdp-project-updates.app.cloud.gov/knowledge-center/"
                  >
                    View Knowledge Center
                  </Button>
                </div>
              </div>
            </li>
            <li className="usa-card--header-first padding-bottom-4 desktop:grid-col-6 mobile:grid-col-12">
              <div className="usa-card__container">
                <header className="usa-card__header">
                  <h3 className="usa-card__heading">
                    Transmission File Layouts & Edits
                  </h3>
                </header>
                <div className="usa-card__body">
                  <p>
                    All transmission file layouts and edits (i.e. error codes)
                    for TANF and SSP-MOE data reporting.
                  </p>
                </div>
                <div className="usa-card__footer">
                  <Button
                    type="button"
                    class="usa-button"
                    id="viewLayoutsButton"
                    href="https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits"
                  >
                    View Layouts & Edits
                  </Button>
                </div>
              </div>
            </li>
            <li className="usa-card--header-first desktop:padding-right-2 desktop:padding-bottom-0 desktop:grid-col-6 mobile:grid-col-12 mobile:padding-bottom-4">
              <div className="usa-card__container">
                <header className="usa-card__header">
                  <h3 className="usa-card__heading">
                    Tribal TANF Data Coding Instructions
                  </h3>
                </header>
                <div className="usa-card__body">
                  <p>
                    File coding instructions addressing each data point that
                    Tribal TANF grantees are required to report upon.
                  </p>
                </div>
                <div className="usa-card__footer">
                  <Button
                    type="button"
                    class="usa-button"
                    id="viewTribalCodingInstructions"
                    href="https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions"
                  >
                    View Tribal TANF Coding Instructions
                  </Button>
                </div>
              </div>
            </li>
            <li className="usa-card--header-first desktop:grid-col-6 mobile:grid-col-12">
              <div className="usa-card__container">
                <header className="usa-card__header">
                  <h3 className="usa-card__heading">
                    ACF-199 and ACF-209 Instructions
                  </h3>
                </header>
                <div className="usa-card__body">
                  <p>
                    Instructions and definitions for completion of forms ACF-199
                    (TANF Data Report) and ACF-209 (SSP-MOE Data Report).
                  </p>
                </div>
                <div className="usa-card__footer">
                  <Button
                    type="button"
                    class="usa-button"
                    id="viewACFFormInstructions"
                    href="https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_data_reports_tan_ssp_instructions_definitions.pdf"
                  >
                    View ACF Form Instructions
                  </Button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </section>
  )
}

export default ResourceCards
