import React from 'react'
import { shallow } from 'enzyme'

import Reports from './Reports'
import Button from '../Button'

describe('Reports', () => {
  it('should render the USWDS Select component with three options', () => {
    const wrapper = shallow(<Reports />)

    const select = wrapper.find('.usa-select')

    expect(select).toExist()

    const options = wrapper.find('option')

    expect(options.length).toEqual(3)
  })

  it('should change route to `/reports/:year/upload` on click of `Begin Report` button', () => {
    const wrapper = shallow(<Reports />)

    const beginButton = wrapper.find(Button)

    expect(beginButton).toExist()

    beginButton.simulate('click')

    expect(window.location.href.includes('/reports/2020/upload')).toBeTruthy()
  })

  it('should update h2 when a new year is selected', () => {
    const wrapper = shallow(<Reports />)

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        value: 2019,
      },
    })

    const h2 = wrapper.find('h2')

    expect(h2.text()).toEqual('2019 TANF Reports')
  })

  it('should render the correct number of options', () => {
    const wrapper = shallow(<Reports />)

    const options = wrapper.find('option')

    expect(options.length).toEqual(3)
  })
})
