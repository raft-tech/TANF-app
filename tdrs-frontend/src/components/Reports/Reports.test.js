import React from 'react'
import { shallow } from 'enzyme'

import Reports from './Reports'
import Button from '../Button'

describe('Reports', () => {
  it('should render an h1 with text All Reports', () => {
    const wrapper = shallow(<Reports />)

    const h1 = wrapper.find('h1')

    expect(h1.text()).toEqual('All Reports')
  })

  it('should render the USWDS Select component with three options', () => {
    const wrapper = shallow(<Reports />)

    const select = wrapper.find('.usa-select')

    expect(select).toExist()

    const options = wrapper.find('option')

    expect(options.length).toEqual(4)
  })

  it('should change route to `/reports/upload` on click of `Begin Report` button', () => {
    const wrapper = shallow(<Reports />)

    const beginButton = wrapper.find(Button)

    expect(beginButton).toExist()

    beginButton.simulate('click')

    expect(window.location.href.includes('/reports/upload')).toBeTruthy()
  })
})
