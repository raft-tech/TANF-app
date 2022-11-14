import { useSelector } from 'react-redux'
import { selectUserPermissions } from '../../selectors/auth'

const isAllowed = (userPermissions, requiredPermissions) => {
  if (!requiredPermissions) {
    return true
  }

  for (var i = 0; i < requiredPermissions.length; i++) {
    if (!userPermissions.includes(requiredPermissions[i])) {
      return false
    }
  }

  return true
}

const PermissionGuard = ({
  children,
  requiredPermissions,
  notAllowedComponent = null,
}) => {
  const userPermissions = useSelector(selectUserPermissions)

  return isAllowed(userPermissions, requiredPermissions)
    ? children
    : notAllowedComponent
}

export default PermissionGuard
