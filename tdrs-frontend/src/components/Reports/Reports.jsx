import React from 'react'
import Button from '../Button'
import { history } from '../../configureStore'

function Reports() {
  const handleClick = () => {
    history.push('/reports/upload')
  }
  return (
    <div className="grid-container">
      <h1 className="font-serif-2xl margin-bottom-0 text-normal">
        All Reports
      </h1>
      <form className="usa-form">
        {/* eslint-disable-next-line */}
        <label className="usa-label margin-top-4" htmlFor="reports">
          Reporting Year
        </label>

        <select className="usa-select" name="options" id="reports">
          <option value>- Select -</option>
          <option value="value1">Option A</option>
          <option value="value2">Option B</option>
          <option value="value3">Option C</option>
        </select>

        <h2 className="font-serif-xl margin-y-4 text-normal">
          2020 TANF Reports
        </h2>

        <p className="font-sans-lg margin-0 text-bold">Test Quarter</p>
        <p className="font-sans-md margin-0 margin-bottom-105">
          Upload by a date
        </p>

        <Button type="button" onClick={handleClick}>
          Begin Report
        </Button>
      </form>
    </div>
  )
}

export default Reports
