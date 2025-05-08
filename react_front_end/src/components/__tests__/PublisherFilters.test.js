import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { PublisherFilters } from "../PublisherFilters"

describe("PublisherFilters", () => {
  const mockCheckboxData = [
    { name: "publisher1", label: "Publisher One" },
    { name: "publisher2", label: "Publisher Two" },
    { name: "publisher3", label: "Publisher Three" },
  ]

  const mockSetCheckedState = jest.fn()
  const mockSetQueryParams = jest.fn()
  const mockSetIsLoading = jest.fn()

  const renderComponent = (checkedState = [false, false, false]) => {
    render(
      <PublisherFilters
        checkboxGroupName="publishers"
        checkboxData={mockCheckboxData}
        checkedState={checkedState}
        setCheckedState={mockSetCheckedState}
        setQueryParams={mockSetQueryParams}
        setIsLoading={mockSetIsLoading}
      />,
    )
  }

  it("renders the component with initial data", () => {
    renderComponent()

    // Check that all publishers are rendered
    expect(screen.getByLabelText("Publisher One")).toBeInTheDocument()
    expect(screen.getByLabelText("Publisher Two")).toBeInTheDocument()
    expect(screen.getByLabelText("Publisher Three")).toBeInTheDocument()
  })

  it("filters the list based on the search query", () => {
    renderComponent()

    // Type into the search input
    const searchInput = screen.getByPlaceholderText("Search")
    fireEvent.change(searchInput, { target: { value: "Two" } })

    // Check that only the matching publisher is displayed
    expect(screen.queryByLabelText("Publisher One")).not.toBeInTheDocument()
    expect(screen.getByLabelText("Publisher Two")).toBeInTheDocument()
    expect(screen.queryByLabelText("Publisher Three")).not.toBeInTheDocument()
  })

  it("checks and unchecks checkboxes", () => {
    renderComponent()

    // Check the first checkbox
    const checkbox = screen.getByLabelText("Publisher One")
    fireEvent.click(checkbox)

    // Ensure the state update functions are called
    expect(mockSetCheckedState).toHaveBeenCalled()
    expect(mockSetQueryParams).toHaveBeenCalled()
    expect(mockSetIsLoading).toHaveBeenCalled()
  })
})
