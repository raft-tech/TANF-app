import React from 'react'
import PropTypes from 'prop-types'

function FileUpload({ file, onUpload }) {
  return (
    <div
      className={`usa-form-group ${file.error ? 'usa-form-group--error' : ''}`}
    >
      <label className="usa-label text-bold" htmlFor="activeData">
        Section 1 - Active Case Data
        <div className="usa-hint" id={`${file.name}-specific-hint`}>
          Select CSV, TXT, or XLS files
        </div>
        <div>
          {file.error && (
            <div
              className="usa-error-message"
              id={`${file.name}-error-alert`}
              role="alert"
            >
              {file.error.message}
            </div>
          )}
        </div>
        <input
          onChange={(e) => onUpload(e)}
          id={file.name}
          className="usa-file-input"
          type="file"
          name={file.name}
          aria-describedby={`${file.name}-specific-hint`}
          accept=".csv,.txt,.xls"
          data-errormessage="We can’t process that file format. Please provide a .txt, .xls, or .csv file."
        />
      </label>
    </div>
  )
}

FileUpload.propTypes = {
  file: PropTypes.shape({
    name: PropTypes.string.isRequired,
    file: PropTypes.string,
    error: PropTypes.shape({
      message: PropTypes.string,
    }),
  }).isRequired,
  onUpload: PropTypes.func.isRequired,
}

export default FileUpload
