import { NextRequest, NextResponse } from "next/server";

/**
 * File download API route
 *
 * Proxies file downloads from the LangGraph backend to the frontend.
 * This avoids CORS issues and provides a clean API for downloading generated files.
 *
 * Backend: http://localhost:8123/files/{path}
 * Frontend: /api/files/{path}
 */
export const runtime = "edge";

const BACKEND_URL = process.env.LANGGRAPH_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8123";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  try {
    // Await params as required by Next.js 15
    const { path } = await params;

    // Reconstruct the file path from URL segments
    const filePath = path.join("/");

    // Build the backend URL
    const backendUrl = `${BACKEND_URL}/files/${filePath}`;

    console.log(`Proxying file request to: ${backendUrl}`);

    // Fetch from backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: {
        // Forward relevant headers
        "Accept": request.headers.get("Accept") || "*/*",
      },
    });

    if (!response.ok) {
      console.error(`Backend returned ${response.status}: ${response.statusText}`);
      return NextResponse.json(
        { error: "File not found or inaccessible" },
        { status: response.status }
      );
    }

    // Get content type from response
    const contentType = response.headers.get("Content-Type") || "application/octet-stream";

    // Get file content
    const blob = await response.blob();

    // Return the file with appropriate headers
    return new NextResponse(blob, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": response.headers.get("Content-Disposition") || "attachment",
        "Cache-Control": "public, max-age=3600",
      },
    });
  } catch (error) {
    console.error("Error proxying file request:", error);
    return NextResponse.json(
      { error: "Failed to fetch file from backend" },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
