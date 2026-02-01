import { NextRequest, NextResponse } from "next/server";

/**
 * API route to proxy review document requests to the backend LangGraph server.
 *
 * This route allows the frontend to fetch review markdown files that are
 * generated during human-in-the-loop workflow steps.
 *
 * Review documents are generated at:
 * - Step 6: recoding_rules_review.md
 * - Step 11: indicators_review.md
 * - Step 14: table_specs_review.md
 */

export const runtime = "edge";

const BACKEND_URL = process.env.LANGGRAPH_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8123";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;

  // Construct the path to the review document
  // The path will be like "recoding_rules_review.md" or "indicators_review.md"
  const docPath = path.join("/");
  const reviewUrl = `${BACKEND_URL}/reviews/${docPath}`;

  try {
    const response = await fetch(reviewUrl);

    if (!response.ok) {
      return NextResponse.json(
        { error: `Failed to fetch review document: ${response.statusText}` },
        { status: response.status }
      );
    }

    // Get the markdown content
    const content = await response.text();

    // Return as markdown
    return new NextResponse(content, {
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "no-cache, no-store, must-revalidate",
      },
    });
  } catch (error) {
    console.error("Error fetching review document:", error);
    return NextResponse.json(
      { error: "Failed to fetch review document from backend" },
      { status: 500 }
    );
  }
}
