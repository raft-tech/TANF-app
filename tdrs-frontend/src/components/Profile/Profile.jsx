import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import UserProfileView from './UserProfileView'
import axiosInstance from '../../axios-instance'
import {
  accountHasPendingProfileChange,
  accountIsInReview,
  accountIsMissingAccessRequest,
  selectUser,
} from '../../selectors/auth'
import { JURISDICTION_TYPES } from './JurisdictionLocationInfo'

function Profile({
  isEditing = false,
  onEdit,
  type,
  user,
  sttList = [],
  onCancel,
  setInEditMode,
}) {
  const authUser = useSelector(selectUser)
  const resolvedUser = user ?? authUser
  const isAMSUser = resolvedUser?.email?.includes('@acf.hhs.gov')
  const userPermissions =
    resolvedUser?.permissions?.map((p) => p.codename) || []
  const hasFRAAccess = userPermissions.includes('has_fra_access')
  const userId = resolvedUser?.id

  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview)
  const isProfileChangePending = useSelector(accountHasPendingProfileChange)
  const [pendingChangeRequests, setPendingChangeRequests] = useState([])

  useEffect(() => {
    if (setInEditMode) {
      setInEditMode(isEditing, type)
    }
  }, [isEditing, type, setInEditMode])

  useEffect(() => {
    let isMounted = true

    const loadPendingChangeRequests = async () => {
      if (!userId || type !== 'profile' || !isProfileChangePending) {
        if (isMounted) {
          setPendingChangeRequests([])
        }
        return
      }

      try {
        const response = await axiosInstance.get(
          `${process.env.REACT_APP_BACKEND_URL}/change-requests/`,
          { withCredentials: true }
        )
        const data = response?.data?.results ?? response?.data ?? []
        const pendingRequests = Array.isArray(data)
          ? data.filter(
              (request) =>
                request?.user === userId && request?.status === 'pending'
            )
          : []
        if (isMounted) {
          setPendingChangeRequests(pendingRequests)
        }
      } catch (error) {
        if (isMounted) {
          setPendingChangeRequests([])
        }
      }
    }

    loadPendingChangeRequests()

    return () => {
      isMounted = false
    }
  }, [userId, type, isProfileChangePending])

  if (isEditing) {
    return (
      <RequestAccessForm
        user={resolvedUser}
        sttList={sttList}
        editMode={isEditing}
        initialValues={{
          firstName: resolvedUser?.first_name || '',
          lastName: resolvedUser?.last_name || '',
          stt: resolvedUser?.stt?.name || '',
          hasFRAAccess: hasFRAAccess ?? null,
          regions: resolvedUser?.regions || new Set(),
          jurisdictionType: resolvedUser?.stt?.type || JURISDICTION_TYPES.STATE,
        }}
        onCancel={onCancel}
        type={type}
      />
    )
  }

  if (missingAccessRequest) {
    return <RequestAccessForm user={resolvedUser} sttList={sttList} />
  }

  return (
    <UserProfileView
      user={resolvedUser}
      isAMSUser={isAMSUser}
      isAccessRequestPending={isAccessRequestPending}
      isProfileChangePending={isProfileChangePending}
      pendingChangeRequests={pendingChangeRequests}
      onEdit={onEdit}
      type={type}
      hasFRAAccess={hasFRAAccess ?? null}
    />
  )
}

export default Profile
