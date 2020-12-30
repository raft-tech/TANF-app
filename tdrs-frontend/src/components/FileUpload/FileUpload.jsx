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
      <label className="usa-label text-bold" htmlFor="activeData">
        Section {section} - {file.name}
        <div className="usa-hint" id={`${file.name}-specific-hint`}>
          Select CSV, TXT, or XLS files
        </div>
        <div>
          {file.error && (
            <div
              className="usa-error-message"
              id={`${transformName(file.name)}-error-alert`}
              role="alert"
            >
              {file.error.message}
            </div>
          )}
        </div>
        <input
          onChange={(e) => onUpload(e)}
          id={transformName(file.name)}
          className="usa-file-input"
          type="file"
          name={transformName(file.name)}
          aria-describedby={`${transformName(file.name)}-specific-hint`}
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
  section: PropTypes.string.isRequired,
}

export default FileUpload
