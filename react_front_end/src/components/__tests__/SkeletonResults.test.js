import React from "react"
import { render, screen } from "@testing-library/react"
import "@testing-library/jest-dom"
import { SkeletonResults } from "../SkeletonResults"

describe("SkeletonResults", () => {
  test("renders 10 skeleton items", () => {
    render(<SkeletonResults />)
    const skeletonItems = screen.getAllByRole("listitem")
    expect(skeletonItems).toHaveLength(10)
  })
})
