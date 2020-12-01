import React from 'react'
import { useDispatch } from 'react-redux'
import Button from '../Button'

import { upload } from '../../actions/upload'

function NewReport() {
  const dispatch = useDispatch()
  const testFunc = (e) => {
    e.preventDefault()
    dispatch(upload(JSON.stringify({ file: e.target.files[0] })))
  }

  return (
    <div className="grid-container margin-top-4">
      <h1 className="font-serif-2xl margin-bottom-0 text-normal">
        New Sample Report 2020
      </h1>
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
    </div>
  )
}

export default NewReport
