import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { LoaderCircle, CheckCircle2, XCircle, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useStreamContext } from "@/providers/Stream";
import { useQueryState } from "nuqs";
import { toast } from "sonner";

export type ReviewType = "recoding" | "indicators" | "table_specs";

interface ReviewDocumentProps {
  reviewType: ReviewType;
  interruptData?: {
    type: string;
    step: number;
    task: string;
    review_document_path: string;
    validation_passed: boolean;
    iteration: number;
    message: string;
  };
}

const reviewTypeTitles: Record<ReviewType, string> = {
  recoding: "Recoding Rules Review",
  indicators: "Indicators Review",
  table_specs: "Table Specifications Review",
};

const reviewTypeDescriptions: Record<ReviewType, string> = {
  recoding: "Review the AI-generated recoding rules for transforming survey variables. These rules will be applied to create the new dataset.",
  indicators: "Review the AI-generated indicators that group related survey variables into semantic categories for analysis.",
  table_specs: "Review the AI-generated table specifications that define the cross-tabulations for statistical analysis.",
};

/**
 * ReviewDocument component displays a markdown review document and provides
 * approve/reject actions for human-in-the-loop workflow steps.
 *
 * This component:
 * 1. Fetches and displays a markdown review document
 * 2. Shows validation status (passed/failed)
 * 3. Provides Approve/Reject with feedback buttons
 * 4. Submits user decision to the backend
 * 5. Resumes workflow after decision
 */
export function ReviewDocument({ reviewType, interruptData }: ReviewDocumentProps) {
  const [content, setContent] = useState<string>("");
  const [feedback, setFeedback] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stream = useStreamContext();
  const [threadId] = useQueryState("threadId");

  useEffect(() => {
    const fetchReviewDocument = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Determine the document name based on review type
        // Maps to: recoding_rules_review.md, indicators_review.md, table_specs_review.md
        const docNames: Record<ReviewType, string> = {
          recoding: "recoding_rules_review.md",
          indicators: "indicators_review.md",
          table_specs: "table_specs_review.md",
        };

        const docName = docNames[reviewType];

        // Fetch from our API route which proxies to the backend
        const response = await fetch(`/api/reviews/${docName}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch review document: ${response.statusText}`);
        }

        const text = await response.text();
        setContent(text);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        toast.error("Failed to load review document", {
          description: errorMessage,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviewDocument();
  }, [reviewType, interruptData]);

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      // Submit approval to backend via the LangGraph API
      // This updates the state and resumes the workflow
      if (!threadId) {
        throw new Error("No thread ID available");
      }

      // Use the feedback endpoint to submit approval via the API proxy
      await fetch(`/api/threads/${threadId}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          approved: true,
          feedback: null,
          iteration_count: interruptData?.iteration,
        }),
      });

      toast.success("Review approved", {
        description: "Workflow will continue to the next step.",
      });

      // Resume the workflow
      await fetch(`/api/threads/${threadId}/resume`, {
        method: "POST",
      });

      // Clear the review document state (will be handled by parent)
      setFeedback("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      toast.error("Failed to submit approval", {
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      if (!threadId) {
        throw new Error("No thread ID available");
      }

      if (!feedback.trim()) {
        toast.error("Feedback required", {
          description: "Please provide feedback for rejection.",
        });
        setIsSubmitting(false);
        return;
      }

      // Submit rejection with feedback via the API proxy
      await fetch(`/api/threads/${threadId}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          approved: false,
          feedback: feedback.trim(),
          iteration_count: interruptData?.iteration,
        }),
      });

      toast.success("Feedback submitted", {
        description: "The workflow will regenerate with your feedback.",
      });

      // Resume the workflow
      await fetch(`/api/threads/${threadId}/resume`, {
        method: "POST",
      });

      setFeedback("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      toast.error("Failed to submit feedback", {
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8 border rounded-lg bg-gray-50">
        <LoaderCircle className="h-6 w-6 animate-spin text-gray-400 mr-2" />
        <span className="text-gray-600">Loading review document...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 border border-red-200 rounded-lg bg-red-50">
        <div className="flex items-center text-red-800 mb-2">
          <XCircle className="h-5 w-5 mr-2" />
          <span className="font-medium">Error loading review document</span>
        </div>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    );
  }

  const validationPassed = interruptData?.validation_passed ?? false;

  return (
    <div className="review-document border rounded-lg bg-white overflow-hidden">
      {/* Header */}
      <div className="border-b bg-gray-50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5 text-gray-600" />
            <div>
              <h3 className="font-semibold text-gray-900">
                {reviewTypeTitles[reviewType]}
              </h3>
              <p className="text-sm text-gray-600 mt-0.5">
                {reviewTypeDescriptions[reviewType]}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {interruptData?.iteration !== undefined && interruptData.iteration > 0 && (
              <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
                Iteration {interruptData.iteration + 1}
              </span>
            )}
            {validationPassed ? (
              <span className="flex items-center gap-1 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                <CheckCircle2 className="h-3 w-3" />
                Validation Passed
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                <XCircle className="h-3 w-3" />
                Validation Failed
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Review Document Content */}
      <div className="p-6 max-h-[600px] overflow-y-auto">
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>

      {/* Review Actions */}
      <div className="border-t bg-gray-50 p-6">
        <div className="space-y-4">
          {/* Feedback Input */}
          <div className="space-y-2">
            <Label htmlFor="feedback">
              Feedback (required for rejection)
            </Label>
            <Textarea
              id="feedback"
              placeholder="Describe what needs to be changed in the regenerated artifact..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-gray-500">
              Provide specific feedback for regeneration. Leave empty if approving.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <Button
              onClick={handleApprove}
              disabled={isSubmitting}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="h-4 w-4 animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Approve
                </>
              )}
            </Button>
            <Button
              onClick={handleReject}
              disabled={isSubmitting || !feedback.trim()}
              variant="destructive"
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="h-4 w-4 animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject with Feedback
                </>
              )}
            </Button>
          </div>

          {/* Instructions */}
          <div className="text-xs text-gray-500 bg-blue-50 border border-blue-200 rounded-md p-3">
            <strong className="text-blue-900">Instructions:</strong>
            <ul className="mt-1 space-y-1 list-disc list-inside text-blue-800">
              <li><strong>Approve:</strong> The artifact looks correct. The workflow will proceed to the next step.</li>
              <li><strong>Reject with Feedback:</strong> The artifact needs changes. Provide specific feedback and it will be regenerated.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
