import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { Search } from "../Search"

describe("Search", () => {
  const mockHandleSearchChange = jest.fn()
  const mockHandleSearchSubmit = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test("renders search input and button", () => {
    render(
      <Search handleSearchChange={mockHandleSearchChange} searchInput="" handleSearchSubmit={mockHandleSearchSubmit} />,
    )

    expect(screen.getByLabelText("Search input")).toBeInTheDocument()
    expect(screen.getByLabelText("Submit search")).toBeInTheDocument()
  })

  test("calls handleSearchChange when input value changes", () => {
    render(
      <Search handleSearchChange={mockHandleSearchChange} searchInput="" handleSearchSubmit={mockHandleSearchSubmit} />,
    )

    fireEvent.change(screen.getByLabelText("Search input"), { target: { value: "test" } })
    expect(mockHandleSearchChange).toHaveBeenCalled()
  })

  test("calls handleSearchSubmit when form is submitted", () => {
    render(
      <Search handleSearchChange={mockHandleSearchChange} searchInput="" handleSearchSubmit={mockHandleSearchSubmit} />,
    )

    fireEvent.submit(screen.getByRole("button", { name: /submit search/i }))
    expect(mockHandleSearchSubmit).toHaveBeenCalled()
  })
})
