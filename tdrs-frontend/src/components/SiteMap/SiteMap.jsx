import React, { useRef, useState } from 'react'
import { useSelector } from 'react-redux'


const isMemberOfOne = (user, ...groupNames) =>
      !!user?.roles?.some((role) => groupNames.includes(role.name))

const userAccessRequestApproved = (user) => !!(!user?.['access_request']) && user.roles.length > 0

const canViewAdmin = (user) =>
      userAccessRequestApproved(user) &&
      isMemberOfOne(user,'Developer', 'OFA System Admin', 'ACF OCIO')

const SiteMap = ({ user }) => (
  <div className="margin-top-5">
    <SiteMap.Link text="Home" link="/home" />
    <SiteMap.Link
      text="Privacy Policy"
      link="https://www.acf.hhs.gov/privacy-policy"
    />
    <SiteMap.Link text="Data Files" link="/data-files" />
    <SiteMap.Link text="Profile" link="/profile" />

    {canViewAdmin(user) && (
      <SiteMap.Link
        text="Admin"
        link={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
      />
    )}
  </div>
)

SiteMap.Link = ({ text, link }) => (
  <a
    className="usa-footer__primary-link"
    href={link}
    target="_blank"
    rel="noopener noreferrer"
  >
    {text}
  </a>
)

export default SiteMap
