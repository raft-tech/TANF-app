import React from 'react'
import { render, screen } from '@testing-library/react'
import TanfSspReports from './TanfSspReports'

const mockUseReportsContext = jest.fn()
const mockFeedbackReportAlert = jest.fn()
const mockSectionSubmissionHistory = jest.fn()

jest.mock('../ReportsContext', () => ({
  useReportsContext: () => mockUseReportsContext(),
}))

jest.mock('../components/Explainers', () => ({
  FiscalQuarterExplainer: () => <div data-testid="fiscal-quarter-explainer" />,
}))

jest.mock('../../FileUploadForms/SectionFileUploadForm', () => () => (
  <div data-testid="section-file-upload-form" />
))

jest.mock('../../SubmissionHistory/SectionSubmissionHistory', () => (props) => {
  mockSectionSubmissionHistory(props)
  return <div data-testid="section-submission-history" />
})

jest.mock('../../SegmentedControl', () => () => (
  <div data-testid="segmented-control" />
))

jest.mock('../components/FiscalYearSelect', () => () => (
  <div data-testid="fiscal-year-select" />
))

jest.mock('../components/FisclaQuarterSelect', () => () => (
  <div data-testid="fiscal-quarter-select" />
))

jest.mock('../../FeedbackReports/FeedbackReportAlert', () => ({
  __esModule: true,
  default: (props) => {
    mockFeedbackReportAlert(props)
    return require('react').createElement('div', {
      'data-testid': 'feedback-report-alert',
    })
  },
}))

describe('TanfSspReports feedback report alert', () => {
  const defaultContext = {
    yearInputValue: '2025',
    quarterInputValue: 'Q1',
    fileTypeInputValue: 'tanf',
    selectedSubmissionTab: 1,
    setSelectedSubmissionTab: jest.fn(),
    setReprocessedModalVisible: jest.fn(),
    setReprocessedDate: jest.fn(),
    headerRef: React.createRef(),
    localAlert: { active: false, message: null },
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseReportsContext.mockReturnValue(defaultContext)
  })

  it('passes TANF_SSP alert report type for state STTs', () => {
    render(
      <TanfSspReports
        stt={{ id: 1, name: 'Wisconsin', type: 'state' }}
        isDataAnalyst={true}
        isRegionalStaff={false}
        canSubmitSsp={true}
      />
    )

    expect(screen.getByTestId('feedback-report-alert')).toBeInTheDocument()
    expect(mockFeedbackReportAlert).toHaveBeenCalledWith(
      expect.objectContaining({
        stt: null,
        reportType: 'TANF_SSP',
      })
    )
  })

  it('passes TRIBAL_TANF alert report type for tribal STTs', () => {
    render(
      <TanfSspReports
        stt={{ id: 12, name: 'Ho-Chunk Nation', type: 'tribe' }}
        isDataAnalyst={true}
        isRegionalStaff={false}
        canSubmitSsp={true}
      />
    )

    expect(screen.getByTestId('feedback-report-alert')).toBeInTheDocument()
    expect(mockFeedbackReportAlert).toHaveBeenCalledWith(
      expect.objectContaining({
        stt: null,
        reportType: 'TRIBAL_TANF',
      })
    )
  })

  it('passes selected STT to alert for regional staff', () => {
    const stt = { id: 12, name: 'Ho-Chunk Nation', type: 'tribe' }

    render(
      <TanfSspReports
        stt={stt}
        isDataAnalyst={false}
        isRegionalStaff={true}
        canSubmitSsp={true}
      />
    )

    expect(screen.getByTestId('feedback-report-alert')).toBeInTheDocument()
    expect(mockFeedbackReportAlert).toHaveBeenCalledWith(
      expect.objectContaining({
        stt,
        reportType: 'TRIBAL_TANF',
      })
    )
  })

  it('renders SSP as history-only when the selected STT cannot submit SSP', () => {
    const setSelectedSubmissionTab = jest.fn()
    mockUseReportsContext.mockReturnValue({
      ...defaultContext,
      fileTypeInputValue: 'ssp-moe',
      selectedSubmissionTab: 1,
      setSelectedSubmissionTab,
    })

    render(
      <TanfSspReports
        stt={{ id: 33, name: 'New York', type: 'state' }}
        isDataAnalyst={false}
        isRegionalStaff={false}
        canSubmitSsp={false}
      />
    )

    expect(screen.getByText('Submission History')).toBeInTheDocument()
    expect(screen.queryByTestId('segmented-control')).not.toBeInTheDocument()
    expect(screen.queryByTestId('section-file-upload-form')).not.toBeInTheDocument()
    expect(screen.getByTestId('section-submission-history')).toBeInTheDocument()
    expect(setSelectedSubmissionTab).toHaveBeenCalledWith(2)
    expect(mockSectionSubmissionHistory).toHaveBeenCalledWith(
      expect.objectContaining({
        filterValues: expect.objectContaining({ file_type: 'ssp-moe' }),
      })
    )
  })

  it('restores the upload tab for TANF even when SSP cannot be submitted', () => {
    mockUseReportsContext.mockReturnValue(defaultContext)

    render(
      <TanfSspReports
        stt={{ id: 33, name: 'New York', type: 'state' }}
        isDataAnalyst={false}
        isRegionalStaff={false}
        canSubmitSsp={false}
      />
    )

    expect(screen.getByTestId('segmented-control')).toBeInTheDocument()
    expect(screen.getByTestId('section-file-upload-form')).toBeInTheDocument()
    expect(screen.queryByTestId('section-submission-history')).not.toBeInTheDocument()
  })
})
