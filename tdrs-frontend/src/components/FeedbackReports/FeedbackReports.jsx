import { useSelector } from 'react-redux'
import { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { useSearchParams } from 'react-router-dom'
import { accountCanUploadFeedbackReports } from '../../selectors/auth'
import AdminFeedbackReports from './AdminFeedbackReports'
import STTFeedbackReports from './STTFeedbackReports'

const REPORT_VIEWS = [
  { manageReports: true, label: 'Manage Feedback Reports' },
  { manageReports: false, label: 'Feedback Reports' },
]

function FeedbackReportsNavigation({ showManageReports, onSelectView }) {
  // Reserve the missing STT subtitle's space so the toggle stays in position.
  // TODO: Consider adding a subtitle instead of margin here.
  const spacing = showManageReports ? '' : 'margin-top-9'

  return (
    <nav
      aria-label="Feedback report views"
      className={`display-flex flex-justify-start ${spacing}`}
    >
      <ul className="usa-list--unstyled display-flex flex-wrap margin-0">
        {REPORT_VIEWS.map(({ manageReports, label }) => {
          const active = showManageReports === manageReports
          return (
            <li className="margin-right-4" key={label}>
              <button
                type="button"
                onClick={() => onSelectView(manageReports)}
                className={`usa-button usa-button--unstyled display-block margin-0 padding-y-2 padding-x-0 text-bold text-base-dark border-bottom-05 ${active ? 'border-primary' : 'border-transparent'}`}
                aria-current={active ? 'page' : undefined}
              >
                <span>{label}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}

FeedbackReportsNavigation.propTypes = {
  showManageReports: PropTypes.bool.isRequired,
  onSelectView: PropTypes.func.isRequired,
}

/**
 * FeedbackReports wrapper component that conditionally renders
 * the appropriate view based on user permissions.
 *
 * - Admin users (with upload permissions) switch between management and STT views
 * - Data Analysts and Regional Staff see the read-only report view
 */
function FeedbackReports() {
  const canUpload = useSelector(accountCanUploadFeedbackReports)
  const [searchParams, setSearchParams] = useSearchParams()
  const [showManageReports, setShowManageReports] = useState(
    () => searchParams.get('view') !== 'stt'
  )

  useEffect(() => {
    setShowManageReports(searchParams.get('view') !== 'stt')
  }, [searchParams])

  const selectView = (manageReports, stt = null, reportContext = null) => {
    const params = new URLSearchParams(searchParams)
    if (manageReports) {
      params.delete('view')
      params.delete('stt')
    } else {
      params.set('view', 'stt')
      if (stt && reportContext) {
        params.set('stt', stt.id)
        params.set('year', reportContext.year)
        params.set('type', reportContext.reportType)
      }
    }
    setShowManageReports(manageReports)
    setSearchParams(params)
  }

  const selectStt = (stt, context) => {
    selectView(false, stt, context)
  }

  if (!canUpload) return <STTFeedbackReports />

  return (
    <>
      <FeedbackReportsNavigation
        showManageReports={showManageReports}
        onSelectView={selectView}
      />
      {showManageReports ? (
        <AdminFeedbackReports onSelectStt={selectStt} />
      ) : (
        <STTFeedbackReports adminView />
      )}
    </>
  )
}

export default FeedbackReports
