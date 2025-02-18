import React from "react"
import { render, screen } from "@testing-library/react"
import "@testing-library/jest-dom"
import { Results } from "../Results"
import { SkeletonResults } from "../SkeletonResults"

jest.mock("../SkeletonResults", () => ({
  SkeletonResults: () => <div data-testid="skeleton-results" />,
}))

describe("Results", () => {
  const mockResults = [
    {
      id: 1,
      type: "Guidance",
      title: "Test Document 1",
      description: "This is a test document description.",
      publisher: "Test Publisher",
      date_modified: "2023-01-01",
      date_valid: "2023-01-01",
      regulatory_topics: ["Topic 1", "Topic 2"],
    },
    {
      id: 2,
      type: "Regulation",
      title: "Test Document 2",
      description: "Another test document description.",
      publisher: "Another Publisher",
      date_modified: "2023-02-01",
      date_valid: "2023-02-01",
      regulatory_topics: ["Topic 3"],
    },
  ]

  test("renders SkeletonResults when isLoading is true", () => {
    render(<Results results={[]} isLoading={true} searchQuery="" />)
    expect(screen.getByTestId("skeleton-results")).toBeInTheDocument()
  })

  test("renders results when isLoading is false", () => {
    render(<Results results={mockResults} isLoading={false} searchQuery="" />)
    expect(screen.getByText("Test Document 1")).toBeInTheDocument()
    expect(screen.getByText("Test Document 2")).toBeInTheDocument()
  })

  // test("highlights search query in title and description", () => {
  //   render(<Results results={mockResults} isLoading={false} searchQuery="test" />)
  //   expect(screen.getByText("Test Document 1")).toBeInTheDocument()
  //   expect(screen.getByText("Test Document 2")).toBeInTheDocument()
  //   expect(screen.getByText("This is a test document description.")).toBeInTheDocument()
  //   expect(screen.getByText("Another test document description.")).toBeInTheDocument()
  // })

  test("renders regulatory topics", () => {
    render(<Results results={mockResults} isLoading={false} searchQuery="" />)
    expect(screen.getByText("Topic 1")).toBeInTheDocument()
    expect(screen.getByText("Topic 2")).toBeInTheDocument()
    expect(screen.getByText("Topic 3")).toBeInTheDocument()
  })

  test("formats date to GOV.UK style", () => {
    render(<Results results={mockResults} isLoading={false} searchQuery="" />)
    expect(screen.getByText("Last updated: 1 January 2023")).toBeInTheDocument()
    expect(screen.getByText("Last updated: 1 February 2023")).toBeInTheDocument()
  })
})
