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
jest.mock("../../components/CheckboxFilter", () => ({
  CheckboxFilter: ({ checkboxData, checkedState, setCheckedState, setQueryParams, withSearch, setIsLoading }) => (
    <div>
      {checkboxData.map((item, index) => (
        <label key={item.name}>
          <input
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
          {item.label}
        </label>
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
  Pagination: ({ pageData, pageQuery, setPageQuery }) => (
    <div>
      <button onClick={() => setPageQuery([pageQuery - 1])}>Previous</button>
      <button onClick={() => setPageQuery([pageQuery + 1])}>Next</button>
    </div>
  ),
}))
jest.mock("../../components/SortSelect", () => ({
  SortSelect: ({ sortQuery, setSortQuery }) => (
    <select value={sortQuery} onChange={(e) => setSortQuery([e.target.value])}>
      <option value="recent">Recently updated</option>
      <option value="relevance">Relevance</option>
    </select>
  ),
}))

describe("App", () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  test("renders the App component", async () => {
    fetch.mockResponseOnce(JSON.stringify({ results: [] }))
    fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })

    await waitFor(() => {
      render(<App />)
    })

    expect(screen.getByLabelText("Search input")).toBeInTheDocument()
    expect(screen.getByText("Document type")).toBeInTheDocument()
    expect(screen.getByText("Published by")).toBeInTheDocument()
    // expect(screen.getByText("Sort by")).toBeInTheDocument()
  })

  //   test("handles search input and submit", async () => {
  //     fetch.mockResponseOnce(JSON.stringify({ results: [] }))
  //     fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })

  //     await waitFor(() => {
  //       render(<App />)
  //     })

  //     fireEvent.change(screen.getByLabelText("Search input"), { target: { value: "test" } })
  //     fireEvent.click(screen.getByText("Search"))

  //     await waitFor(() => {
  //       expect(fetchData).toHaveBeenCalledWith({
  //         search: "test",
  //         document_type: [],
  //         publisher: [],
  //         sort: "recent",
  //         page: [1],
  //       })
  //     })
  //   })

  //   test("handles filter changes", async () => {
  //     fetch.mockResponseOnce(JSON.stringify({ results: [] }))
  //     fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })

  //     await waitFor(() => {
  //       render(<App />)
  //     })

  //     fireEvent.click(screen.getByLabelText("Document type 1"))
  //     await waitFor(() => {
  //       expect(fetchData).toHaveBeenCalledWith({
  //         search: "",
  //         document_type: ["Document type 1"],
  //         publisher: [],
  //         sort: "recent",
  //         page: [1],
  //       })
  //     })
  //   })

  //   test("handles pagination", async () => {
  //     fetch.mockResponseOnce(JSON.stringify({ results: [] }))
  //     fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })

  //     await waitFor(() => {
  //       render(<App />)
  //     })

  //     fireEvent.click(screen.getByText("Next"))
  //     await waitFor(() => {
  //       expect(fetchData).toHaveBeenCalledWith({
  //         search: "",
  //         document_type: [],
  //         publisher: [],
  //         sort: "recent",
  //         page: [2],
  //       })
  //     })
  //   })

  //   test("handles sorting", async () => {
  //     fetch.mockResponseOnce(JSON.stringify({ results: [] }))
  //     fetchData.mockResolvedValueOnce({ results: [], start_index: 0, end_index: 0, results_total_count: 0 })

  //     await waitFor(() => {
  //       render(<App />)
  //     })

  //     fireEvent.change(screen.getByLabelText("Sort by"), { target: { value: "relevance" } })
  //     await waitFor(() => {
  //       expect(fetchData).toHaveBeenCalledWith({
  //         search: "",
  //         document_type: [],
  //         publisher: [],
  //         sort: "relevance",
  //         page: [1],
  //       })
  //     })
  //   })
})
