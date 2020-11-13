import React from 'react'
import axios from 'axios'
import { shallow } from 'enzyme'
import { render } from '@testing-library/react'

import { act } from 'react-dom/test-utils'
import IdleTimer from './IdleTimer'

describe('IdleTimer', () => {
  it('should have a modal with an id of "myModal"', () => {
    const wrapper = shallow(<IdleTimer />)

    const modal = wrapper.find('#myModal')

    expect(modal).toExist()
  })

  it('should start with a className of display-none', () => {
    const wrapper = shallow(<IdleTimer />)

    const modal = wrapper.find('#myModal')

    expect(modal.hasClass('display-none')).toBeTruthy()
  })

  it('should change to a className of display-block after 2 seconds', () => {
    jest.useFakeTimers()
    const { container } = render(<IdleTimer />)

    const modal = container.querySelector('#myModal')

    act(() => {
      jest.runAllTimers()
    })

    expect(modal.classList.contains('display-block')).toBeTruthy()
  })

  it('should change window location to sign out url when sign out button is clicked on session timeout modal', () => {
    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = shallow(<IdleTimer />)

    const signOutButton = wrapper.find('.sign-out')

    expect(signOutButton).toExist()

    signOutButton.simulate('click')

    expect(window.location.href).toEqual(url)
  })

  it('should call an axios post method when `Stay Signed In` button is clicked', () => {
    axios.post.mockImplementationOnce(() => Promise.resolve('hello'))

    const wrapper = shallow(<IdleTimer />)

    const staySignedInButton = wrapper.find('.renew-session')

    staySignedInButton.simulate('click')

    expect(axios.post).toHaveBeenCalledTimes(1)
  })
})
