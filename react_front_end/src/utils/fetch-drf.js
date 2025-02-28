import { SEARCH_URL, PUBLISHERS } from "./constants"

function buildQuery(filters) {
  const { search, document_type, publisher, sort, page } = filters

  const searchQuery = search && search.length > 2 ? `query=${search}` : ""
  const documentTypeQuery = document_type ? document_type.map((type) => `document_type=${type}`).join("&") : ""
  const publisherQuery = publisher ? publisher.map((pub) => `publisher=${pub}`).join("&") : ""
  const pageQuery = page ? `page=${page}` : ""
  const sortQuery = sort ? `sort=${sort}` : ""

  let query = [searchQuery, documentTypeQuery, publisherQuery, pageQuery, sortQuery]
    .filter((q) => q.length > 0)
    .join("&")

  return query
}

export async function fetchData(filters) {
  const query = buildQuery(filters)

  const url = `${SEARCH_URL}?${query}`

  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error("Network response was not ok")
    }
    const data = await response.json()
    return data
  } catch (error) {
    console.error("There was a problem with your fetch operation:", error)
  }
}
