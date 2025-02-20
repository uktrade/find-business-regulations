import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { AppliedFilters } from "../AppliedFilters"
import { DOCUMENT_TYPES } from "../../utils/constants"

describe("AppliedFilters", () => {
  const mockRemoveFilter = jest.fn()
  const publishers = [
    { name: "Publisher 1", label: "Publisher 1" },
    { name: "Publisher 2", label: "Publisher 2" },
  ]

  test("renders applied document type filters", () => {
    const documentTypeCheckedState = [true, false]
    const publisherCheckedState = [false, false]

    render(
      <AppliedFilters
        documentTypeCheckedState={documentTypeCheckedState}
        publisherCheckedState={publisherCheckedState}
        removeFilter={mockRemoveFilter}
        publishers={publishers}
      />,
    )

    expect(screen.getByText(DOCUMENT_TYPES[0].label)).toBeInTheDocument()
    expect(screen.queryByText(DOCUMENT_TYPES[1].label)).not.toBeInTheDocument()
  })

  test("renders applied publisher filters", () => {
    const documentTypeCheckedState = [false, false]
    const publisherCheckedState = [true, false]

    render(
      <AppliedFilters
        documentTypeCheckedState={documentTypeCheckedState}
        publisherCheckedState={publisherCheckedState}
        removeFilter={mockRemoveFilter}
        publishers={publishers}
      />,
    )

    expect(screen.getByText(publishers[0].label)).toBeInTheDocument()
    expect(screen.queryByText(publishers[1].label)).not.toBeInTheDocument()
  })

  test("calls removeFilter when a filter is clicked", () => {
    const documentTypeCheckedState = [true, false]
    const publisherCheckedState = [false, false]

    render(
      <AppliedFilters
        documentTypeCheckedState={documentTypeCheckedState}
        publisherCheckedState={publisherCheckedState}
        removeFilter={mockRemoveFilter}
        publishers={publishers}
      />,
    )

    fireEvent.click(screen.getByText(DOCUMENT_TYPES[0].label))
    expect(mockRemoveFilter).toHaveBeenCalledWith("docType", DOCUMENT_TYPES[0].name)
  })
})
