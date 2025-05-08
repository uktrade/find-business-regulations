import React from "react"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import "@testing-library/jest-dom"
import App from "../../App"
import { fetchData } from "../../utils/fetch-drf"

jest.mock("../../utils/fetch-drf")
jest.mock("../../components/Search", () => ({
  Search: ({ handleSearchChange, searchInput, handleSearchSubmit }) => (
    <div>
      <input aria-label="Search input" value={searchInput} onChange={handleSearchChange} />
      <button onClick={handleSearchSubmit}>Search</button>
    </div>
  ),
}))
jest.mock("../../components/DocTypeFilters", () => ({
  DocTypeFilters: ({ checkboxData, checkedState, setCheckedState, setQueryParams, setIsLoading }) => (
    <div>
      {checkboxData.map((item, index) => (
        <div key={item.name}>
          <input
            id={`checkbox-${item.name}`}
            type="checkbox"
            checked={checkedState[index]}
            onChange={() => {
              const newState = [...checkedState]
              newState[index] = !newState[index]
              setCheckedState(newState)
              setQueryParams(newState.filter((checked, i) => checked).map((_, i) => checkboxData[i].name))
              setIsLoading(true)
            }}
          />
          <label htmlFor={`checkbox-${item.name}`}>{item.label}</label>
        </div>
      ))}
    </div>
  ),
}))
jest.mock("../../components/Results", () => ({
  Results: ({ results, isLoading, searchQuery }) => (
    <div>{isLoading ? "Loading..." : results.map((result) => <div key={result.id}>{result.title}</div>)}</div>
  ),
}))
jest.mock("../../components/ResultsCount", () => ({
  ResultsCount: ({ isLoading, start, end, totalResults }) => (
    <div>{isLoading ? "Loading..." : `${start} to ${end} of ${totalResults} results`}</div>
  ),
}))
jest.mock("../../components/Pagination", () => ({
  Pagination: ({ pageData, pageQuery, setPageQuery }) => {
    return (
      <div>
        <button onClick={() => setPageQuery([parseInt(pageQuery) - 1])}>Previous</button>
        <button onClick={() => setPageQuery([parseInt(pageQuery) + 1])}>Next</button>
      </div>
    )
  },
}))
jest.mock("../../components/SortSelect", () => ({
  SortSelect: ({ sortQuery, setSortQuery }) => (
    <select aria-label="Sort by" value={sortQuery} onChange={(e) => setSortQuery([e.target.value])}>
      <option value="recent">Recently updated</option>
      <option value="relevance">Relevance</option>
    </select>
  ),
}))

describe("App", () => {
  beforeEach(() => {
    fetch.resetMocks()
    fetchData.mockClear()
    fetch.mockResponseOnce(JSON.stringify({ results: [] }))
    fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })
  })

  test("renders the App component", async () => {
    await waitFor(() => {
      render(<App />)
    })

    expect(screen.getByLabelText("Search input")).toBeInTheDocument()
    expect(screen.getByText("Document type")).toBeInTheDocument()
    expect(screen.getByText("Published by")).toBeInTheDocument()
  })

  test("handles search input and submit", async () => {
    await waitFor(() => {
      render(<App />)
    })

    fireEvent.change(screen.getByLabelText("Search input"), { target: { value: "test" } })
    fireEvent.click(screen.getByText("Search"))

    await waitFor(() => {
      expect(fetchData).toHaveBeenCalledWith({
        search: "test",
        sort: "relevance",
        page: [1],
      })
    })
  })

  test("handles document type filter changes", async () => {
    await waitFor(() => {
      render(<App />)
    })

    fireEvent.click(screen.getByLabelText("Legislation"))
    await waitFor(() => {
      expect(fetchData).toHaveBeenCalledWith({
        search: "test",
        sort: "relevance",
        document_type: ["legislation"],
        page: [1],
      })
    })
  })

  test("handles pagination", async () => {
    await waitFor(() => {
      render(<App />)
    })

    fireEvent.click(screen.getByText("Next"))
    await waitFor(() => {
      expect(fetchData).toHaveBeenCalledWith({
        search: "test",
        sort: "relevance",
        document_type: ["legislation"],
        page: [2],
      })
    })
  })

  test("handles sorting", async () => {
    await waitFor(() => {
      render(<App />)
    })

    fireEvent.change(screen.getByLabelText("Sort by"), { target: { value: "relevance" } })
    await waitFor(() => {
      expect(fetchData).toHaveBeenCalledWith({
        search: "test",
        sort: "relevance",
        document_type: ["legislation"],
        page: [2],
      })
    })
  })
})
