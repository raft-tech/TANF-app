import React, { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import fileInput from 'uswds/src/js/components/file-input'
import Button from '../Button'

import { upload } from '../../actions/upload'

function UploadReport() {
  const dispatch = useDispatch()
  const testFunc = (e) => {
    dispatch(upload({ file: e.target.files[0] }))
  }

  useEffect(() => {
    fileInput.init()
  })

  return (
    <form>
      <div className="usa-form-group">
        {/* eslint-disable-next-line */}
          <label className="usa-label text-bold" htmlFor="file-input-single">
          Section 1 - Active Case Data
        </label>
        <input
          onChange={testFunc}
          id="file-input-single"
          className="usa-file-input"
          type="file"
          name="file-input-single"
        />
      </div>
      <div className="usa-form-group">
        {/* eslint-disable-next-line */}
          <label className="usa-label text-bold" htmlFor="file-input-single">
          Section 2 - Closed Case Data
        </label>
        <input
          onChange={testFunc}
          id="file-input-single"
          className="usa-file-input"
          type="file"
          name="file-input-single"
        />
      </div>
      <div className="usa-form-group">
        {/* eslint-disable-next-line */}
          <label className="usa-label text-bold" htmlFor="file-input-single">
          Section 3 - Aggregate Data
        </label>
        <input
          onChange={testFunc}
          id="file-input-single"
          className="usa-file-input"
          type="file"
          name="file-input-single"
        />
      </div>
      <div className="usa-form-group">
        {/* eslint-disable-next-line */}
          <label className="usa-label text-bold" htmlFor="file-input-single">
          Section 4 - Stratum Data
        </label>
        <input
          onChange={testFunc}
          id="file-input-single"
          className="usa-file-input"
          type="file"
          name="file-input-single"
        />
      </div>
      <div className="buttonContainer margin-y-4">
        <Button type="submit">Submit Files</Button>
        <Button type="button">Cancel</Button>
      </div>
    </form>
  )
}

export default UploadReport
