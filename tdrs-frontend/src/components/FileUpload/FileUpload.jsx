import React from 'react'
import PropTypes from 'prop-types'

function FileUpload({ file, section, onUpload }) {
  const transformName = (name) => {
    const splitName = name.split(' ')
    return `${splitName[0].toLowerCase()}${splitName[1]}`
  }

  return (
    <div
      className={`usa-form-group ${file.error ? 'usa-form-group--error' : ''}`}
    >
      <label className="usa-label text-bold" htmlFor={file.section}>
        Section {section} - {file.section}
        <div className="usa-hint" id={`${file.section}-specific-hint`}>
          Select CSV, TXT, or XLS files
        </div>
        <div>
          {file.error && (
            <div
              className="usa-error-message"
              id={`${transformName(file.section)}-error-alert`}
              role="alert"
            >
              {file.error.message}
            </div>
          )}
        </div>
        <input
          onChange={(e) => onUpload(e)}
          id={transformName(file.section)}
          className="usa-file-input"
          type="file"
          name={file.section}
          aria-describedby={`${transformName(file.section)}-specific-hint`}
          accept=".csv,.txt,.xls"
          data-errormessage="We can’t process that file format. Please provide a .txt, .xls, or .csv file."
        />
      </label>
    </div>
  )
}

FileUpload.propTypes = {
  file: PropTypes.shape({
    section: PropTypes.string.isRequired,
    file: PropTypes.string,
    error: PropTypes.shape({
      message: PropTypes.string,
    }),
  }).isRequired,
  onUpload: PropTypes.func.isRequired,
  section: PropTypes.string.isRequired,
}

export default FileUpload
