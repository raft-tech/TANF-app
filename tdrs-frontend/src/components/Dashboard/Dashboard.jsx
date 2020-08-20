import React from 'react'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import { useSelector } from 'react-redux'

function Dashboard() {
  const user = useSelector((state) => state.auth.user)
  const handleClick = (event) => {
    event.preventDefault()
    window.location = 'https://tdp-backend.app.cloud.gov/v1/logout/oidc'
  }
  return (
    <GridContainer className="welcome">
      <Grid row>
        <Grid col={7} className="left">
          <h1>
            Welcome {user}!
            <span role="img" aria-label="wave" aria-hidden="true">
              {' '}
              🎉
            </span>
          </h1>
        </Grid>
        <Grid col={5} className="right">
          <Button type="button" size="big" onClick={handleClick}>
            Sign Out
          </Button>
        </Grid>
      </Grid>
    </GridContainer>
  )
}

export default Dashboard
