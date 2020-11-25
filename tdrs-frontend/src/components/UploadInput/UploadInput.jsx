import React from 'react'

function UploadInput() {
  const testFunc = (e) => {
    e.preventDefault()
    console.log('HERE', e.target.files)
  }

  return (
    <div className="grid-container margin-top-4">
      <form>
        <div className="usa-form-group">
          <label className="usa-label" htmlFor="file-input-single">
            Input accepts a single file
          </label>
          <input
            onChange={testFunc}
            id="file-input-single"
            className="usa-file-input"
            type="file"
            name="file-input-single"
          />
        </div>
        <button type="submit" className="margin-4">
          Submit
        </button>
      </form>
    </div>
  )
}

export default UploadInput
