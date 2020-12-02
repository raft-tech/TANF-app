import React, { useState } from 'react'
import Button from '../Button'
import { history } from '../../configureStore'

function Reports() {
  const [selectedYear, setSelectedYear] = useState(2020)

  const handleClick = () => {
    history.push(`/reports/${selectedYear}/upload`)
  }

  const handleSelect = ({ target: { value } }) => {
    setSelectedYear(value)
  }

  const createOptions = (years) => {
    let yearsBack = years
    const options = []
    let currentYear = 2020

    do {
      yearsBack -= 1
      options.push(<option key={currentYear}>{currentYear}</option>)
      currentYear -= 1
    } while (yearsBack > 0)

    return options
  }
  return (
    <form className="usa-form">
      {/* eslint-disable-next-line */}
        <label className="usa-label text-bold margin-top-4" htmlFor="reports">
        Reporting Year
      </label>
      {/* eslint-disable-next-line */}
        <select
        className="usa-select"
        name="options"
        id="reports"
        onChange={handleSelect}
      >
        {createOptions(3)}
      </select>

      <h2 className="font-serif-xl margin-y-4 text-normal">
        {selectedYear} TANF Reports
      </h2>

      <p className="font-sans-md margin-0 text-bold">Test Quarter</p>
      <p className="font-sans-md margin-0 margin-bottom-105">
        Upload by a date
      </p>

      <Button type="button" onClick={handleClick}>
        Begin Report
      </Button>
    </form>
  )
}

export default Reports
