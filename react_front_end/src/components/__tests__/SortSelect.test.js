import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { SortSelect } from "../SortSelect"

describe("SortSelect", () => {
  const mockSetSortQuery = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test("renders sort select with correct options", () => {
    render(<SortSelect sortQuery="recent" setSortQuery={mockSetSortQuery} />)

    expect(screen.getByLabelText("Sort by")).toBeInTheDocument()
    expect(screen.getByText("Recently updated")).toBeInTheDocument()
    expect(screen.getByText("Relevance")).toBeInTheDocument()
  })

  test("calls setSortQuery with the selected option", () => {
    render(<SortSelect sortQuery="recent" setSortQuery={mockSetSortQuery} />)

    fireEvent.change(screen.getByLabelText("Sort by"), { target: { value: "relevance" } })
    expect(mockSetSortQuery).toHaveBeenCalledWith(["relevance"])
  })

  test("selects the correct option based on sortQuery prop", () => {
    render(<SortSelect sortQuery="relevance" setSortQuery={mockSetSortQuery} />)

    expect(screen.getByLabelText("Sort by").value).toBe("relevance")
  })
})
