import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import fileInput from 'uswds/src/js/components/file-input'
import Button from '../Button'

import { clearError, upload } from '../../actions/upload'

function UploadReport() {
  const files = useSelector((state) => state.upload.files)
  const dispatch = useDispatch()
  const testFunc = ({ target }) => {
    dispatch(clearError({ name: target.name }))
    dispatch(upload({ file: target.files[0], name: target.name }))
      .then((resp) => resp)
      .then((success) => {
        if (!success) {
          const inputTarget = target.parentNode
          const previewHeading = inputTarget.querySelector(
            '.usa-file-input__preview-heading'
          )
          const preview = inputTarget.querySelector('.usa-file-input__preview')
          const instructions = inputTarget.querySelector(
            '.usa-file-input__instructions'
          )
          inputTarget.removeChild(previewHeading)
          inputTarget.removeChild(preview)
          instructions.classList.remove('display-none')
        }
      })
  }

  useEffect(() => {
    fileInput.init()
  }, [])

  return (
    <form>
      <div
        className={`usa-form-group ${
          files[0].error ? 'usa-form-group--error' : ''
        }`}
      >
        <label className="usa-label text-bold" htmlFor="activeData">
          Section 1 - Active Case Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV, TXT, or XLS files
          </div>
          <div>
            {files[0].error && (
              <div
                className="usa-error-message"
                id="file-input-error-alert"
                role="alert"
              >
                {files[0].error.message}
              </div>
            )}
          </div>
          <input
            onChange={(e) => testFunc(e)}
            id="activeData"
            className="usa-file-input"
            type="file"
            name="activeData"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt,.xls"
          />
        </label>
      </div>
      <div
        className={`usa-form-group ${
          files[1].error ? 'usa-form-group--error' : ''
        }`}
      >
        <label className="usa-label text-bold" htmlFor="closedData">
          Section 2 - Closed Case Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV, TXT, or XLS files
          </div>
          <div>
            {files[1].error && (
              <div
                className="usa-error-message"
                id="file-input-error-alert"
                role="alert"
              >
                {files[1].error.message}
              </div>
            )}
          </div>
          <input
            onChange={testFunc}
            id="closedData"
            className="usa-file-input"
            type="file"
            name="closedData"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt,.xls"
          />
        </label>
      </div>
      <div
        className={`usa-form-group ${
          files[2].error ? 'usa-form-group--error' : ''
        }`}
      >
        <label className="usa-label text-bold" htmlFor="aggregateData">
          Section 3 - Aggregate Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV, TXT, or XLS files
          </div>
          <div>
            {files[2].error && (
              <div
                className="usa-error-message"
                id="file-input-error-alert"
                role="alert"
              >
                {files[2].error.message}
              </div>
            )}
          </div>
          <input
            onChange={testFunc}
            id="aggregataData"
            className="usa-file-input"
            type="file"
            name="aggregataData"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt,.xls"
          />
        </label>
      </div>
      <div
        className={`usa-form-group ${
          files[3].error ? 'usa-form-group--error' : ''
        }`}
      >
        <label className="usa-label text-bold" htmlFor="stratumData">
          Section 4 - Stratum Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV, TXT, or XLS files
          </div>
          <div>
            {files[3].error && (
              <div
                className="usa-error-message"
                id="file-input-error-alert"
                role="alert"
              >
                {files[3].error.message}
              </div>
            )}
          </div>
          <input
            onChange={testFunc}
            id="stratumData"
            className="usa-file-input"
            type="file"
            name="stratumData"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt,.xls"
          />
        </label>
      </div>
      <div className="buttonContainer margin-y-4">
        <Button type="submit">Submit Files</Button>
        <Button type="button">Cancel</Button>
      </div>
    </form>
  )
}

export default UploadReport
