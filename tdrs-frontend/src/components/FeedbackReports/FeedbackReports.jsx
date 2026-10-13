import { useSelector } from 'react-redux'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { accountCanUploadFeedbackReports } from '../../selectors/auth'
import AdminFeedbackReports from './AdminFeedbackReports'
import STTFeedbackReports from './STTFeedbackReports'

/**
 * FeedbackReports wrapper component that conditionally renders
 * the appropriate view based on user permissions.
 *
 * - Admin users (with upload permissions) see the upload interface
 * - STT Data Analysts see the read-only view with download capability
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

  if (canUpload) {
    return (
      <>
        <nav
          aria-label="Feedback report views"
          className="display-flex flex-justify-end"
        >
          <ul className="usa-list--unstyled display-flex margin-0">
            {[
              [true, 'Manage Feedback Reports', showManageReports],
              [false, 'Feedback Reports', !showManageReports],
            ].map(([manageReports, label, active]) => (
              <li key={label}>
                <button
                  type="button"
                  onClick={() => selectView(manageReports)}
                  className={`usa-button usa-button--unstyled display-block padding-2 text-bold text-base-dark border-bottom-05 ${active ? 'border-primary' : 'border-transparent'}`}
                  aria-current={active ? 'page' : undefined}
                >
                  <span>{label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
        {showManageReports ? (
          <AdminFeedbackReports
            onSelectStt={(stt, context) => selectView(false, stt, context)}
          />
        ) : (
          <STTFeedbackReports adminView />
        )}
      </>
    )
  }

  return <STTFeedbackReports />
}

export default FeedbackReports
