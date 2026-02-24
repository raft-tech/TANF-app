import axios from 'axios'
import { render } from '@testing-library/react'
import {
  SubmissionSummaryStatusIcon,
  downloadErrorReport,
  fileStatusOrDefault,
  formatProgramType,
  getErrorReportStatus,
  getReprocessedDate,
  getSummaryStatusLabel,
  hasReparsed,
} from './helpers'
import { getParseErrors } from '../../actions/createXLSReport'
import {
  faCheckCircle,
  faClock,
  faExclamationCircle,
  faXmarkCircle,
} from '@fortawesome/free-solid-svg-icons'

jest.mock('axios')
jest.mock('../../actions/reports', () => ({
  download: jest.fn(),
}))
jest.mock('../../actions/createXLSReport', () => ({
  getParseErrors: jest.fn(),
}))

describe('formatProgramType', () => {
  it('returns a label for SSP', () => {
    expect(formatProgramType('SSP')).toEqual('SSP')
  })

  it('returns a label for Tribal', () => {
    expect(formatProgramType('TRIBAL')).toEqual('Tribal')
  })

  it('returns a label for FRA', () => {
    expect(formatProgramType('FRA')).toEqual('FRA')
  })

  it('returns empty string for unknown program type', () => {
    expect(formatProgramType('UNKNOWN')).toEqual('')
  })
})

describe('downloadErrorReport', () => {
  it('downloads and parses error report data', async () => {
    axios.get.mockResolvedValue({ data: 'blob-data' })
    const file = { id: 123 }

    await downloadErrorReport(file, 'report-name')

    expect(axios.get).toHaveBeenCalledWith(
      `${process.env.REACT_APP_BACKEND_URL}/data_files/123/download_error_report/`,
      { responseType: 'blob' }
    )
    expect(getParseErrors).toHaveBeenCalledWith('blob-data', 'report-name')
  })

  it('logs when download fails', async () => {
    const logSpy = jest.spyOn(console, 'log').mockImplementation(() => {})
    axios.get.mockRejectedValue(new Error('fail'))

    await downloadErrorReport({ id: 456 }, 'report-name')

    expect(logSpy).toHaveBeenCalled()
    logSpy.mockRestore()
  })
})

describe('getErrorReportStatus', () => {
  const baseFile = {
    summary: { status: 'Accepted' },
    program_type: 'TAN',
    year: 2024,
    quarter: 'Q1',
    section: 'Active Case Data',
  }

  it('returns a download button when errors exist', () => {
    const file = { ...baseFile, hasError: true }
    const { container } = render(getErrorReportStatus(file))
    const button = container.querySelector('button.section-download')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent(
      '2024-Q1-TANF Active Case Data Error Report.xlsx'
    )
  })

  it('returns No Errors when completed without errors', () => {
    const file = { ...baseFile, hasError: false }
    expect(getErrorReportStatus(file)).toEqual('No Errors')
  })

  it('returns Pending for pending status', () => {
    const file = { ...baseFile, summary: { status: 'Pending' } }
    expect(getErrorReportStatus(file)).toEqual('Pending')
  })
})

describe('SubmissionSummaryStatusIcon', () => {
  it('maps Pending to clock icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Pending' })
    expect(element.props.icon).toBe(faClock)
    expect(element.props.color).toBe('#005EA2')
  })

  it('maps Accepted to check icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Accepted' })
    expect(element.props.icon).toBe(faCheckCircle)
    expect(element.props.color).toBe('#40bb45')
  })

  it('maps Accepted with Errors to exclamation icon', () => {
    const element = SubmissionSummaryStatusIcon({
      status: 'Accepted with Errors',
    })
    expect(element.props.icon).toBe(faExclamationCircle)
    expect(element.props.color).toBe('#ec4e11')
  })

  it('maps Rejected to x icon', () => {
    const element = SubmissionSummaryStatusIcon({ status: 'Rejected' })
    expect(element.props.icon).toBe(faXmarkCircle)
    expect(element.props.color).toBe('#bb0000')
  })
})

describe('summary helpers', () => {
  it('detects reparsed files', () => {
    expect(
      hasReparsed({ latest_reparse_file_meta: { finished_at: '2024-01-01' } })
    ).toBe(true)
    expect(hasReparsed({ latest_reparse_file_meta: {} })).toBeFalsy()
  })

  it('returns reprocessed date', () => {
    expect(
      getReprocessedDate({
        latest_reparse_file_meta: { finished_at: '2024-02-02' },
      })
    ).toEqual('2024-02-02')
  })

  it('returns Pending for missing status', () => {
    expect(fileStatusOrDefault(null)).toEqual('Pending')
  })

  it('returns status label for TimedOut', () => {
    const file = { summary: { status: 'TimedOut' } }
    expect(getSummaryStatusLabel(file)).toEqual(
      'Still processing. Check back soon.'
    )
  })
})
