const getCookie = (name) => {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

const signOut = () => {
  const logoutUrl = `${process.env.REACT_APP_BACKEND_URL}/keycloak/logout/`
  const csrfToken = getCookie('csrftoken')

  if (!csrfToken) {
    console.error('CSRF token not found.')
    return
  }

  // Create a form
  const form = document.createElement('form')
  form.method = 'POST'
  form.action = logoutUrl

  // Add CSRF token
  const csrfInput = document.createElement('input')
  csrfInput.type = 'hidden'
  csrfInput.name = 'csrfmiddlewaretoken'
  csrfInput.value = csrfToken
  form.appendChild(csrfInput)

  // Append form to body and submit
  document.body.appendChild(form)
  form.submit()
}

export default signOut
