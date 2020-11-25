import React from 'react'
import { Switch, Route } from 'react-router-dom'
import SplashPage from '../SplashPage/SplashPage'
import EditProfile from '../EditProfile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Request from '../Request'
import UploadInput from '../UploadInput'

/**
 * This component renters the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const Routes = () => {
  return (
    <Switch>
      <Route exact path="/">
        <SplashPage />
      </Route>
      <Route>
        <UploadInput />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <PrivateRoute exact path="/edit-profile">
        <EditProfile />
      </PrivateRoute>
      <PrivateRoute exact path="/request">
        <Request />
      </PrivateRoute>
    </Switch>
  )
}

export default Routes
