import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import fileInput from 'uswds/src/js/components/file-input'
import Button from '../Button'

import { clearError, upload } from '../../actions/upload'

function UploadReport() {
  const uploadError = useSelector((state) => state.upload.error)
  const dispatch = useDispatch()
  const testFunc = ({ target }) => {
    dispatch(clearError())
    dispatch(upload({ file: target.files[0] }))
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
          uploadError ? 'usa-form-group--error' : ''
        }`}
      >
        <label className="usa-label text-bold" htmlFor="file-input-specific">
          Section 1 - Active Case Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV or TXT files
          </div>
          <div>
            {uploadError && (
              <div
                className="usa-error-message"
                id="file-input-error-alert"
                role="alert"
              >
                {uploadError.message}
              </div>
            )}
          </div>
          <input
            onChange={testFunc}
            id="firstOne"
            className="usa-file-input"
            type="file"
            name="file-input-specific"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt"
          />
        </label>
      </div>
      <div className="usa-form-group">
        <label className="usa-label text-bold" htmlFor="file-input-specific">
          Section 2 - Closed Case Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV or TXT files
          </div>
          <input
            onChange={testFunc}
            id="file-input-specific"
            className="usa-file-input"
            type="file"
            name="file-input-specific"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt"
          />
        </label>
      </div>
      <div className="usa-form-group">
        <label className="usa-label text-bold" htmlFor="file-input-specific">
          Section 3 - Aggregate Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV or TXT files
          </div>
          <input
            onChange={testFunc}
            id="file-input-specific"
            className="usa-file-input"
            type="file"
            name="file-input-specific"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt"
          />
        </label>
      </div>
      <div className="usa-form-group">
        <label className="usa-label text-bold" htmlFor="file-input-specific">
          Section 4 - Stratum Data
          <div className="usa-hint" id="file-input-specific-hint">
            Select CSV or TXT files
          </div>
          <input
            onChange={testFunc}
            id="file-input-specific"
            className="usa-file-input"
            type="file"
            name="file-input-specific"
            aria-describedby="file-input-specific-hint"
            accept=".csv,.txt"
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
