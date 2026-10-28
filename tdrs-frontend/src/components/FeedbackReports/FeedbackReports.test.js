import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { MemoryRouter, useLocation, useNavigate } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import FeedbackReports from './FeedbackReports'
import { get } from '../../fetch-instance'

jest.mock('../../fetch-instance')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
  datePicker: {
    init: jest.fn(),
  },
  comboBox: {
    init: jest.fn(),
  },
}))

// Mock STTComboBox to avoid fetchSttList side effects
jest.mock('../STTComboBox', () => {
  const MockSTTComboBox = ({ selectStt, selectedStt }) => (
    <div data-testid="stt-combobox">
      <label htmlFor="mock-stt-select">State, Tribe, or Territory*</label>
      <select
        id="mock-stt-select"
        value={selectedStt || ''}
        onChange={(e) => selectStt(e.target.value)}
        aria-label="State, Tribe, or Territory"
      >
        <option value="">- Select or Search -</option>
        <option value="Wisconsin">Wisconsin</option>
        <option value="Example Tribe">Example Tribe</option>
      </select>
    </div>
  )
  MockSTTComboBox.displayName = 'MockSTTComboBox'
  return MockSTTComboBox
})

const mockStore = configureStore([thunk])

function NavigationProbe() {
  const location = useLocation()
  const navigate = useNavigate()
  return (
    <>
      <output data-testid="feedback-location">
        {location.pathname}
        {location.search}
      </output>
      <button type="button" onClick={() => navigate(-1)}>
        Back
      </button>
    </>
  )
}

describe('FeedbackReports', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    get.mockResolvedValue({
      data: { results: [] },
      ok: true,
      status: 200,
      error: null,
    })

    // Mock FileReader for AdminFeedbackReports
    global.FileReader = jest.fn().mockImplementation(() => ({
      readAsArrayBuffer: jest.fn(function () {
        setTimeout(() => this.onload && this.onload(), 0)
      }),
      result: new ArrayBuffer(8),
    }))
  })

  const renderComponent = (
    store,
    entry = '/feedback-reports',
    navigation = false
  ) => {
    return render(
      <MemoryRouter initialEntries={[entry]}>
        <Provider store={store}>
          <FeedbackReports />
          {navigation && <NavigationProbe />}
        </Provider>
      </MemoryRouter>
    )
  }

  describe('Admin view tabs', () => {
    const adminState = {
      auth: {
        authenticated: true,
        user: {
          account_approval_status: 'Approved',
          roles: [
            {
              name: 'DIGIT Team',
              permissions: [
                'view_reportfile',
                'view_reportsource',
                'add_reportsource',
              ].map((codename) => ({ codename })),
            },
          ],
        },
      },
      stts: {
        sttList: [
          { id: 10, name: 'Wisconsin', type: 'state' },
          { id: 20, name: 'Example Tribe', type: 'tribe' },
        ],
        loading: false,
      },
    }

    it('switches from the modal on the existing URL and restores management on Back', async () => {
      get
        .mockResolvedValueOnce({
          ok: true,
          data: {
            results: [
              {
                id: 42,
                created_at: '2026-08-11T14:10:00Z',
                original_filename: 'FY2025.zip',
                date_extracted_on: '2025-09-30',
                status: 'SUCCEEDED',
                downloaded_count: 1,
                total_count: 1,
              },
            ],
          },
        })
        .mockResolvedValueOnce({
          ok: true,
          data: {
            report_source_id: 42,
            downloaded_count: 1,
            total_count: 1,
            regions: [
              {
                id: 1,
                stts: [{ id: 10, name: 'Wisconsin', downloaded_at: null }],
              },
            ],
          },
        })
      renderComponent(
        mockStore(adminState),
        '/feedback-reports?year=2025&type=TANF_SSP',
        true
      )
      fireEvent.click(
        await screen.findByRole('button', {
          name: 'View download statistics for FY2025.zip',
        })
      )
      fireEvent.click(await screen.findByRole('link', { name: 'Wisconsin' }))
      await waitFor(() =>
        expect(get).toHaveBeenCalledWith(expect.stringContaining('/reports/'), {
          params: { stt: 10, year: 2025, report_type: 'TANF_SSP' },
        })
      )
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      const url = screen.getByTestId('feedback-location').textContent
      expect(url.split('?')[0]).toBe('/feedback-reports')
      expect(new URLSearchParams(url.split('?')[1]).get('view')).toBe('stt')
      expect(screen.getByLabelText('State, Tribe, or Territory')).toHaveValue(
        'Wisconsin'
      )
      fireEvent.click(screen.getByRole('button', { name: 'Back' }))
      await waitFor(() =>
        expect(
          screen.getByRole('button', { name: 'Manage Feedback Reports' })
        ).toHaveAttribute('aria-current', 'page')
      )
      expect(screen.getByLabelText('Fiscal Year')).toHaveValue('2025')
    })

    it('switches existing views and searches by selected STT without an assigned STT', async () => {
      renderComponent(mockStore(adminState))
      expect(
        screen.getByRole('button', { name: 'Manage Feedback Reports' })
      ).toHaveAttribute('aria-current', 'page')
      fireEvent.click(screen.getByRole('button', { name: 'Feedback Reports' }))
      expect(
        screen.getByRole('button', { name: 'Feedback Reports' })
      ).toHaveAttribute('aria-current', 'page')
      expect(get).not.toHaveBeenCalled()
      fireEvent.change(screen.getByLabelText('State, Tribe, or Territory'), {
        target: { value: 'Wisconsin' },
      })
      fireEvent.change(screen.getByLabelText(/Fiscal Year/), {
        target: { value: '2025' },
      })
      expect(get).not.toHaveBeenCalled()
      fireEvent.click(screen.getByRole('button', { name: 'Search' }))
      await waitFor(() =>
        expect(get).toHaveBeenCalledWith(expect.stringContaining('/reports/'), {
          params: { stt: 10, year: 2025, report_type: 'TANF_SSP' },
        })
      )
      expect(
        screen.getByRole('heading', { name: /Wisconsin.*2025/ })
      ).toBeInTheDocument()
      fireEvent.change(screen.getByLabelText(/Fiscal Year/), {
        target: { value: '2024' },
      })
      expect(
        screen.getByRole('heading', { name: /Wisconsin.*2025/ })
      ).toBeInTheDocument()
      expect(get).toHaveBeenCalledTimes(1)
    })

    it.each([
      [10, 'TANF_SSP', 'Wisconsin'],
      [10, 'FRA', 'Wisconsin'],
      [20, 'TRIBAL_TANF', 'Example Tribe'],
    ])(
      'loads a preselected STT link for %s and %s',
      async (stt, type, name) => {
        renderComponent(
          mockStore(adminState),
          `/feedback-reports?view=stt&stt=${stt}&year=2025&type=${type}`
        )
        await waitFor(() =>
          expect(get).toHaveBeenCalledWith(
            expect.stringContaining('/reports/'),
            { params: { stt, year: 2025, report_type: type } }
          )
        )
        expect(
          screen.getByRole('heading', { name: new RegExp(`${name}.*2025`) })
        ).toBeInTheDocument()
        expect(
          screen.queryByText('Feedback Reports ZIP')
        ).not.toBeInTheDocument()
      }
    )

    it.each([
      'stt=999&year=2025',
      'stt=10&year=2025invalid',
      'year=2025',
      'stt=10&year=2025&type=unknown',
    ])(
      'does not request unfiltered reports for invalid selections: %s',
      (query) => {
        renderComponent(
          mockStore(adminState),
          `/feedback-reports?view=stt&${query}`
        )
        expect(get).not.toHaveBeenCalled()
      }
    )

    it('waits for the STT list before resolving a deep link', async () => {
      const entry =
        '/feedback-reports?view=stt&stt=20&year=2025&type=TRIBAL_TANF'
      const view = (store) => (
        <MemoryRouter initialEntries={[entry]}>
          <Provider store={store}>
            <FeedbackReports />
          </Provider>
        </MemoryRouter>
      )
      const { rerender } = render(
        view(
          mockStore({
            ...adminState,
            stts: { sttList: [], loading: true },
          })
        )
      )
      expect(get).not.toHaveBeenCalled()
      rerender(view(mockStore(adminState)))
      await waitFor(() =>
        expect(get).toHaveBeenCalledWith(expect.stringContaining('/reports/'), {
          params: { stt: 20, year: 2025, report_type: 'TRIBAL_TANF' },
        })
      )
    })

    it('ignores a late response from an earlier admin search', async () => {
      let resolveFirstSearch
      get.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveFirstSearch = resolve
          })
      )
      renderComponent(
        mockStore(adminState),
        '/feedback-reports?view=stt&stt=10&year=2025&type=TANF_SSP'
      )
      await waitFor(() => expect(get).toHaveBeenCalledTimes(1))
      fireEvent.change(screen.getByLabelText(/Fiscal Year/), {
        target: { value: '2024' },
      })
      fireEvent.click(screen.getByRole('button', { name: 'Search' }))
      await waitFor(() => expect(get).toHaveBeenCalledTimes(2))
      await act(async () =>
        resolveFirstSearch({
          ok: false,
          error: 'Obsolete search failed',
        })
      )
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      expect(
        screen.getByRole('heading', { name: /Wisconsin.*2024/ })
      ).toBeInTheDocument()
    })

    it('ignores the admin view and selected STT query for analysts', async () => {
      renderComponent(
        mockStore({
          ...adminState,
          auth: {
            user: {
              account_approval_status: 'Approved',
              roles: [
                {
                  name: 'Data Analyst',
                  permissions: [{ codename: 'view_reportfile' }],
                },
              ],
              stt: { id: 99, name: 'Assigned STT', type: 'state' },
            },
          },
        }),
        '/feedback-reports?view=stt&stt=10&year=2025'
      )
      expect(
        screen.queryByRole('navigation', { name: 'Feedback report views' })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByLabelText('State, Tribe, or Territory')
      ).not.toBeInTheDocument()
      await waitFor(() =>
        expect(get).toHaveBeenCalledWith(expect.stringContaining('/reports/'), {
          params: { year: 2025, report_type: 'TANF_SSP' },
        })
      )
    })
  })

  describe('Conditional Rendering', () => {
    it('renders AdminFeedbackReports for users with upload permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'admin@example.com',
            roles: [
              {
                name: 'DIGIT Team',
                permissions: [
                  { codename: 'view_reportsource' },
                  { codename: 'add_reportsource' },
                ],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // AdminFeedbackReports has the description and fiscal year selector
      await waitFor(() => {
        expect(
          screen.getByText(/Once submitted, TDP will distribute/)
        ).toBeInTheDocument()
      })

      // Should have the fiscal year selector (Admin page requires year selection)
      expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()

      // Select a fiscal year to reveal the upload section
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      // Now the file upload input should be visible
      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      // Should have the upload button
      expect(
        screen.getByRole('button', { name: /Upload & Notify STTs/i })
      ).toBeInTheDocument()
    })

    it('renders STTFeedbackReports for users without upload permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'analyst@example.com',
            roles: [
              {
                name: 'Data Analyst',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // STTFeedbackReports has the fiscal year selector and reference table
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })

      // Should have the fiscal year selector
      expect(
        screen.getByLabelText(/Fiscal Year \(October - September\)/i)
      ).toBeInTheDocument()

      // Should NOT have the Upload button (that's for OFA admins only)
      expect(
        screen.queryByRole('button', { name: /Upload & Notify STTs/i })
      ).not.toBeInTheDocument()
    })

    it('renders STTFeedbackReports for users with only view_reportsource (no add)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'viewer@example.com',
            roles: [
              {
                name: 'Viewer',
                permissions: [{ codename: 'view_reportsource' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view since they don't have add_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for users with only add_reportsource (no view)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'adder@example.com',
            roles: [
              {
                name: 'Adder',
                permissions: [{ codename: 'add_reportsource' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view since they don't have view_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for users with no permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'noperm@example.com',
            roles: [{ name: 'User', permissions: [] }],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view since they have no upload permissions
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for OFA Regional Staff (not Admin view)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'regional@example.com',
            roles: [
              {
                name: 'OFA Regional Staff',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
            regions: [
              {
                id: 5,
                stts: [{ id: 10, name: 'Wisconsin', type: 'state' }],
              },
            ],
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view (not admin) since regional staff don't have add_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })

      // Should NOT have the Upload button
      expect(
        screen.queryByRole('button', { name: /Upload & Notify STTs/i })
      ).not.toBeInTheDocument()
    })
  })

  describe('Permission-based API calls', () => {
    it('calls report-sources API for admin users after fiscal year selected', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'admin@example.com',
            roles: [
              {
                name: 'DIGIT Team',
                permissions: [
                  { codename: 'view_reportsource' },
                  { codename: 'add_reportsource' },
                ],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Admin page requires fiscal year selection before API call
      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()
      })

      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/report-sources/'),
          expect.objectContaining({
            params: { year: '2025', report_type: 'TANF_SSP' },
          })
        )
      })
    })

    it('calls reports API for STT users after fiscal year selected', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'analyst@example.com',
            roles: [
              {
                name: 'Data Analyst',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
            stt: { id: 1, name: 'Alabama' },
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // STT users must select a fiscal year before reports are fetched
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.any(Object)
        )
      })

      // Make sure it's not calling the report-sources endpoint
      const calls = get.mock.calls
      const reportSourcesCall = calls.find((call) =>
        call[0].includes('report-sources')
      )
      expect(reportSourcesCall).toBeUndefined()
    })
  })
})
