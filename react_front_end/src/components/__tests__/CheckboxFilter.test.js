import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { CheckboxFilter } from "../CheckboxFilter"

describe("CheckboxFilter", () => {
  const mockSetCheckedState = jest.fn()
  const mockSetQueryParams = jest.fn()
  const mockSetIsLoading = jest.fn()

  const checkboxData = [
    { name: "checkbox1", label: "Checkbox 1" },
    { name: "checkbox2", label: "Checkbox 2" },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test("renders checkboxes", () => {
    const checkedState = [false, false]

    render(
      <CheckboxFilter
        checkboxData={checkboxData}
        checkedState={checkedState}
        setCheckedState={mockSetCheckedState}
        setQueryParams={mockSetQueryParams}
        withSearch={false}
        setIsLoading={mockSetIsLoading}
      />,
    )

    expect(screen.getByLabelText("Checkbox 1")).toBeInTheDocument()
    expect(screen.getByLabelText("Checkbox 2")).toBeInTheDocument()
  })

  test("calls setCheckedState and setQueryParams when a checkbox is clicked", () => {
    const checkedState = [false, false]

    render(
      <CheckboxFilter
        checkboxData={checkboxData}
        checkedState={checkedState}
        setCheckedState={mockSetCheckedState}
        setQueryParams={mockSetQueryParams}
        withSearch={false}
        setIsLoading={mockSetIsLoading}
      />,
    )

    fireEvent.click(screen.getByLabelText("Checkbox 1"))
    expect(mockSetCheckedState).toHaveBeenCalledWith([true, false])
    expect(mockSetQueryParams).toHaveBeenCalledWith(["checkbox1"])
    expect(mockSetIsLoading).toHaveBeenCalledWith(true)
  })

  test("filters checkboxes based on search query", () => {
    const checkedState = [false, false]

    render(
      <CheckboxFilter
        checkboxData={checkboxData}
        checkedState={checkedState}
        setCheckedState={mockSetCheckedState}
        setQueryParams={mockSetQueryParams}
        withSearch={true}
        setIsLoading={mockSetIsLoading}
      />,
    )

    fireEvent.change(screen.getByPlaceholderText("Search"), { target: { value: "Checkbox 1" } })
    expect(screen.getByLabelText("Checkbox 1")).toBeInTheDocument()
    expect(screen.queryByLabelText("Checkbox 2")).not.toBeInTheDocument()
  })
})
