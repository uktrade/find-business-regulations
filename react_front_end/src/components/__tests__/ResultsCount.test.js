import React from "react"
import { render, screen } from "@testing-library/react"
import "@testing-library/jest-dom"
import { ResultsCount } from "../ResultsCount"

describe("ResultsCount", () => {
  test("displays loading message when isLoading is true", () => {
    render(<ResultsCount isLoading={true} start={0} end={0} totalResults={0} />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
  })

  test("displays results count when isLoading is false and there are results", () => {
    render(<ResultsCount isLoading={false} start={1} end={10} totalResults={100} />)
    expect(screen.getByText("1 to 10 of 100 results")).toBeInTheDocument()
  })

  test("displays no results message when isLoading is false and there are no results", () => {
    render(<ResultsCount isLoading={false} start={0} end={0} totalResults={0} />)
    expect(screen.getByText("No results found")).toBeInTheDocument()
  })
})
