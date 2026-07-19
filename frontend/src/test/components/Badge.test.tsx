import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Badge from "../../components/ui/Badge";

describe("Badge", () => {
  it("renders its children", () => {
    render(<Badge>Published</Badge>);
    expect(screen.getByText("Published")).toBeInTheDocument();
  });

  it("applies the danger variant styling", () => {
    render(<Badge variant="danger">Suspended</Badge>);
    expect(screen.getByText("Suspended")).toHaveClass("text-red-600");
  });
});
