import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import PasswordStrength from "../../components/PasswordStrength";

describe("PasswordStrength", () => {
  it("renders nothing for an empty password", () => {
    const { container } = render(<PasswordStrength password="" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("labels a short password as too short", () => {
    render(<PasswordStrength password="abc" />);
    expect(screen.getByText("Too short")).toBeInTheDocument();
  });

  it("labels a long mixed-case password with digits and symbols as strong", () => {
    render(<PasswordStrength password="Str0ng!Passw0rd#2026" />);
    expect(screen.getByText("Strong")).toBeInTheDocument();
  });
});
