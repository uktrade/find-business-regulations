import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { DocTypeFilters } from "../DocTypeFilters"

describe("DocTypeFilters", () => {
  const mockCheckboxData = [
    { name: "docType1", label: "Document Type One" },
    { name: "docType2", label: "Document Type Two" },
    { name: "docType3", label: "Document Type Three" },
  ]

  const mockSetCheckedState = jest.fn()
  const mockSetQueryParams = jest.fn()
  const mockSetIsLoading = jest.fn()

  const renderComponent = (checkedState = [false, false, false], withSearch = false) => {
    render(
      <DocTypeFilters
        checkboxGroupName="documentTypes"
        checkboxData={mockCheckboxData}
        checkedState={checkedState}
        setCheckedState={mockSetCheckedState}
        setQueryParams={mockSetQueryParams}
        setIsLoading={mockSetIsLoading}
        withSearch={withSearch}
      />,
    )
  }

  it("renders the component with initial data", () => {
    renderComponent()

    // Check that all document types are rendered
    expect(screen.getByLabelText("Document Type One")).toBeInTheDocument()
    expect(screen.getByLabelText("Document Type Two")).toBeInTheDocument()
    expect(screen.getByLabelText("Document Type Three")).toBeInTheDocument()
  })

  it("checks and unchecks checkboxes", () => {
    renderComponent()

    // Check the first checkbox
    const checkbox = screen.getByLabelText("Document Type One")
    fireEvent.click(checkbox)

    // Ensure the state update functions are called
    expect(mockSetCheckedState).toHaveBeenCalled()
    expect(mockSetQueryParams).toHaveBeenCalled()
    expect(mockSetIsLoading).toHaveBeenCalled()
  })

  it("renders with the correct checked state", () => {
    // Render with the second checkbox checked
    renderComponent([false, true, false])

    // Check the state of the checkboxes
    const checkboxes = screen.getAllByRole("checkbox")
    expect(checkboxes[0]).not.toBeChecked()
    expect(checkboxes[1]).toBeChecked()
    expect(checkboxes[2]).not.toBeChecked()
  })

  it("renders with the correct list ID when withSearch is true", () => {
    renderComponent([false, false, false], true)

    // Check that the list has the correct ID
    const list = screen.getByRole("list")
    expect(list).toHaveAttribute("id", "documentTypes-autocomplete-list")
  })

  it("renders with the correct list ID when withSearch is false", () => {
    renderComponent([false, false, false], false)

    // Check that the list has the correct ID
    const list = screen.getByRole("list")
    expect(list).toHaveAttribute("id", "documentTypes-list")
  })
})
