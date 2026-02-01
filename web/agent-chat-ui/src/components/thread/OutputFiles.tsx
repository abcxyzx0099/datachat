import React from "react";
import { cn } from "@/lib/utils";
import { Download, FileText, Globe, ExternalLink } from "lucide-react";

interface OutputFile {
  type: "powerpoint" | "html";
  path: string;
  filename: string;
}

interface OutputFilesProps {
  powerpointFile?: string | null;
  htmlDashboardFile?: string | null;
  className?: string;
}

/**
 * Extract filename from file path
 */
function getFilename(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

/**
 * Determine if a path is a URL
 */
function isUrl(path: string): boolean {
  return path.startsWith("http://") || path.startsWith("https://");
}

/**
 * Convert backend file path to API proxy URL
 * Backend serves files at http://localhost:8123/files/{path}
 * Frontend proxies through /api/files/{path}
 */
function getFileUrl(path: string): string {
  if (isUrl(path)) {
    return path;
  }
  // Remove leading slash if present and encode path
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  return `/api/files/${encodeURIComponent(cleanPath)}`;
}

/**
 * OutputFiles component displays download links for generated output files.
 *
 * Shows:
 * - PowerPoint presentation (.pptx)
 * - HTML dashboard
 */
export function OutputFiles({
  powerpointFile,
  htmlDashboardFile,
  className,
}: OutputFilesProps) {
  const hasPowerPoint = !!powerpointFile;
  const hasHtmlDashboard = !!htmlDashboardFile;
  const hasAnyOutput = hasPowerPoint || hasHtmlDashboard;

  if (!hasAnyOutput) {
    return null;
  }

  const outputs: OutputFile[] = [];

  if (hasPowerPoint && powerpointFile) {
    outputs.push({
      type: "powerpoint",
      path: powerpointFile,
      filename: getFilename(powerpointFile),
    });
  }

  if (hasHtmlDashboard && htmlDashboardFile) {
    outputs.push({
      type: "html",
      path: htmlDashboardFile,
      filename: getFilename(htmlDashboardFile),
    });
  }

  return (
    <div
      className={cn(
        "w-full bg-gradient-to-br from-green-50 to-blue-50 rounded-lg border-2 border-green-200 p-5",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
          <svg
            className="w-5 h-5 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Analysis Complete!
          </h3>
          <p className="text-sm text-gray-600">
            Your survey analysis reports are ready to download
          </p>
        </div>
      </div>

      {/* Output Files */}
      <div className="space-y-2">
        {outputs.map((output) => (
          <div
            key={output.path}
            className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-3 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  output.type === "powerpoint" &&
                    "bg-orange-100 text-orange-600",
                  output.type === "html" && "bg-blue-100 text-blue-600"
                )}
              >
                {output.type === "powerpoint" ? (
                  <FileText className="w-5 h-5" />
                ) : (
                  <Globe className="w-5 h-5" />
                )}
              </div>
              <div>
                <p className="font-medium text-gray-900 text-sm">
                  {output.type === "powerpoint"
                    ? "PowerPoint Presentation"
                    : "HTML Dashboard"}
                </p>
                <p className="text-xs text-gray-500">{output.filename}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {output.type === "html" ? (
                <a
                  href={getFileUrl(output.path)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                    "bg-blue-600 text-white hover:bg-blue-700"
                  )}
                >
                  <ExternalLink className="w-4 h-4" />
                  Open
                </a>
              ) : (
                <a
                  href={getFileUrl(output.path)}
                  download={output.filename}
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                    "bg-green-600 text-white hover:bg-green-700"
                  )}
                >
                  <Download className="w-4 h-4" />
                  Download
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer note */}
      <p className="text-xs text-gray-500 mt-3">
        Files are stored in the <code className="bg-gray-100 px-1 rounded">output/</code>{" "}
        directory
      </p>
    </div>
  );
}

/**
 * Hook to extract output files from stream values
 */
export function useOutputFiles(streamValues: any): {
  powerpointFile?: string | null;
  htmlDashboardFile?: string | null;
} {
  return {
    powerpointFile: streamValues?.powerpoint_file,
    htmlDashboardFile: streamValues?.html_dashboard_file,
  };
}
