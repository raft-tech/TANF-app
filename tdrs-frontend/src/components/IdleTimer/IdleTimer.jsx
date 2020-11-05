import React, { useState } from 'react'
import { useIdleTimer } from 'react-idle-timer'
// import axios from 'axios'
import Button from '../Button'

function IdleTimer() {
  const [display, setDisplay] = useState(false)

  // const signOut = () => {
  //   window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  // }

  // const staySignedIn = () => {
  //   axios.post('/v1/authorization-check')
  // }

  useIdleTimer({
    timeout: 1000 * 60 * 20,
    onIdle: () => setDisplay(true),
  })

  return (
    <div
      id="myModal"
      className={`modal ${display ? 'display-block' : 'display-none'}`}
    >
      <div className="modal-content">
        <div className="modal-header">
          <h2>Your Session is About to Expire!</h2>
        </div>
        <div className="modal-body">
          <p>
            Your TANF Data Portal session will expire due to inactivity in three
            minutes. Any unsaved data will be lost if you allow the session to
            expire. Click the button below to continue your session.
          </p>
        </div>
        <div className="modal-footer">
          <Button type="button" className="margin-1">
            Sign Out
          </Button>
          <Button type="button" className="margin-1">
            Stay Signed In
          </Button>
        </div>
      </div>
    </div>
  )
}

export default IdleTimer
