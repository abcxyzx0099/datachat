import React from "react";
import { cn } from "@/lib/utils";
import { LoaderCircle } from "lucide-react";

/**
 * 22-step workflow names and descriptions
 */
const STEP_INFO: Record<number, { name: string; description: string }> = {
  1: { name: "Loading Survey Data", description: "Reading SPSS .sav file and extracting raw data" },
  2: { name: "Extracting Metadata", description: "Extracting variable metadata from survey file" },
  3: { name: "Filtering Variables", description: "Filtering variables that require recoding" },
  4: { name: "Generating Recoding Rules", description: "Creating recoding rules for variables" },
  5: { name: "Validating Recoding Rules", description: "Validating generated recoding rules" },
  6: { name: "Reviewing Recoding Rules", description: "Waiting for your approval of recoding rules" },
  7: { name: "Generating PSPP Syntax", description: "Creating PSPP recoding syntax" },
  8: { name: "Creating Recoded Dataset", description: "Generating new recoded dataset" },
  9: { name: "Generating Indicators", description: "Creating indicators from recoded data" },
  10: { name: "Validating Indicators", description: "Validating generated indicators" },
  11: { name: "Reviewing Indicators", description: "Waiting for your approval of indicators" },
  12: { name: "Generating Table Specifications", description: "Creating table specifications" },
  13: { name: "Validating Table Specs", description: "Validating table specifications" },
  14: { name: "Reviewing Table Specs", description: "Waiting for your approval of table specs" },
  15: { name: "Generating CTABLES Syntax", description: "Creating PSPP CTABLES syntax" },
  16: { name: "Generating Cross-Tabs Syntax", description: "Creating PSPP cross-tabulation syntax" },
  17: { name: "Executing PSPP Syntax", description: "Running PSPP syntax to generate tables" },
  18: { name: "Running Statistical Tests", description: "Performing chi-square and z-tests" },
  19: { name: "Filtering Significant Tables", description: "Filtering tables with significant results" },
  20: { name: "Applying Corrections", description: "Applying Bonferroni corrections" },
  21: { name: "Generating PowerPoint", description: "Creating PowerPoint presentation" },
  22: { name: "Generating HTML Dashboard", description: "Creating HTML dashboard" },
};

interface StepIndicatorProps {
  currentStep: number | null;
  className?: string;
}

/**
 * StepIndicator shows the current workflow step being executed.
 * Displays as a subtle indicator above messages when workflow is running.
 */
export function StepIndicator({ currentStep, className }: StepIndicatorProps) {
  if (!currentStep || currentStep < 1 || currentStep > 22) {
    return null;
  }

  const stepInfo = STEP_INFO[currentStep];
  const isReviewStep = [6, 11, 14].includes(currentStep);

  return (
    <div
      className={cn(
        "flex items-center gap-3 text-sm py-2 px-4 rounded-lg",
        isReviewStep
          ? "bg-amber-50 border border-amber-200 text-amber-800"
          : "bg-blue-50 border border-blue-200 text-blue-800",
        className
      )}
    >
      <LoaderCircle className={cn("w-4 h-4", isReviewStep ? "text-amber-600" : "text-blue-600", "animate-spin")} />
      <div className="flex-1">
        <div className="font-medium">
          Step {currentStep}: {stepInfo.name}
        </div>
        <div className="text-xs opacity-80">{stepInfo.description}</div>
      </div>
      {isReviewStep && (
        <span className="text-xs font-semibold px-2 py-1 bg-amber-100 rounded">
          Awaiting Review
        </span>
      )}
    </div>
  );
}
