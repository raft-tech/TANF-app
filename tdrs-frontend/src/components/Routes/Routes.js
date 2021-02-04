import React from 'react'
import { Switch, Route } from 'react-router-dom'
import { useSelector } from 'react-redux'
import SplashPage from '../SplashPage'
import EditProfile from '../EditProfile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Request from '../Request'
import Reports from '../Reports'
import UploadReport from '../UploadReport'

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const Routes = () => {
  const year = useSelector((state) => state.reports.year)
  return (
    <Switch>
      <Route exact path="/">
        <SplashPage />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <PrivateRoute exact title="Request Access" path="/edit-profile">
        <EditProfile />
      </PrivateRoute>
      <PrivateRoute exact title="Request Submitted" path="/request">
        <Request />
      </PrivateRoute>
      <PrivateRoute exact title="TANF Reports" path="/reports">
        <Reports />
      </PrivateRoute>
      <PrivateRoute
        exact
        title={`New TANF Report - ${year}`}
        path="/reports/:year/upload"
      >
        <UploadReport />
      </PrivateRoute>
    </Switch>
  )
}

export default Routes
