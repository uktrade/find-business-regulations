import React from "react"
import { render, screen, fireEvent } from "@testing-library/react"
import "@testing-library/jest-dom"
import { Pagination } from "../Pagination"

describe("Pagination", () => {
  const mockSetPageQuery = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  const pageData = {
    current_page: 2,
    is_paginated: true,
    results_page_total: 5,
  }

  test("renders pagination component", () => {
    render(<Pagination pageData={pageData} pageQuery={[2]} setPageQuery={mockSetPageQuery} />)

    expect(screen.getByLabelText("Previous page")).toBeInTheDocument()
    expect(screen.getByLabelText("Next page")).toBeInTheDocument()
    expect(screen.getByText("1")).toBeInTheDocument()
    expect(screen.getByText("2")).toBeInTheDocument()
    expect(screen.getByText("3")).toBeInTheDocument()
    // expect(screen.getByText("4")).toBeInTheDocument()
    expect(screen.getByText("5")).toBeInTheDocument()
  })

  test("calls setPageQuery with the previous page when previous button is clicked", () => {
    render(<Pagination pageData={pageData} pageQuery={[2]} setPageQuery={mockSetPageQuery} />)

    fireEvent.click(screen.getByLabelText("Previous page"))
    expect(mockSetPageQuery).toHaveBeenCalledWith([1])
  })

  test("calls setPageQuery with the next page when next button is clicked", () => {
    render(<Pagination pageData={pageData} pageQuery={[2]} setPageQuery={mockSetPageQuery} />)

    fireEvent.click(screen.getByLabelText("Next page"))
    expect(mockSetPageQuery).toHaveBeenCalledWith([3])
  })

  test("calls setPageQuery with the correct page number when a page link is clicked", () => {
    render(<Pagination pageData={pageData} pageQuery={[2]} setPageQuery={mockSetPageQuery} />)

    fireEvent.click(screen.getByText("5"))
    expect(mockSetPageQuery).toHaveBeenCalledWith([5])
  })

  test("does not render pagination component when is_paginated is false", () => {
    const nonPaginatedData = { ...pageData, is_paginated: false }
    render(<Pagination pageData={nonPaginatedData} pageQuery={[2]} setPageQuery={mockSetPageQuery} />)

    expect(screen.queryByLabelText("Previous page")).not.toBeInTheDocument()
    expect(screen.queryByLabelText("Next page")).not.toBeInTheDocument()
  })
})
