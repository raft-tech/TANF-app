import React from 'react'

function Reports(props) {
  return (
    <div className="grid-container">
      <h1>All Reports</h1>
      <form className="usa-form">
        {/* eslint-disable-next-line */}
        <label className="usa-label" htmlFor="reports">
          Reporting Year
        </label>
        <select className="usa-select" name="options" id="reports">
          <option value>- Select -</option>
          <option value="value1">Option A</option>
          <option value="value2">Option B</option>
          <option value="value3">Option C</option>
        </select>
      </form>
    </div>
  )
}

export default Reports
