import React from "react";
import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, LoaderCircle } from "lucide-react";

/**
 * 22-step workflow configuration for survey analysis
 * Each step has a name and the phase it belongs to
 */
const WORKFLOW_STEPS = [
  // Phase 1: Data Extraction (Steps 1-3)
  { step: 1, name: "Load survey data", phase: "Data Extraction" },
  { step: 2, name: "Extract variable metadata", phase: "Data Extraction" },
  { step: 3, name: "Filter variables", phase: "Data Extraction" },

  // Phase 2: Recoding (Steps 4-8)
  { step: 4, name: "Generate recoding rules", phase: "Recoding" },
  { step: 5, name: "Validate recoding rules", phase: "Recoding" },
  { step: 6, name: "Review recoding rules", phase: "Recoding" },
  { step: 7, name: "Generate PSPP recoding syntax", phase: "Recoding" },
  { step: 8, name: "Create recoded dataset", phase: "Recoding" },

  // Phase 3: Indicators (Steps 9-11)
  { step: 9, name: "Generate indicators", phase: "Indicators" },
  { step: 10, name: "Validate indicators", phase: "Indicators" },
  { step: 11, name: "Review indicators", phase: "Indicators" },

  // Phase 4: Table Specifications (Steps 12-16)
  { step: 12, name: "Generate table specifications", phase: "Table Specs" },
  { step: 13, name: "Validate table specifications", phase: "Table Specs" },
  { step: 14, name: "Review table specifications", phase: "Table Specs" },
  { step: 15, name: "Generate PSPP ctables syntax", phase: "Table Specs" },
  { step: 16, name: "Generate PSPP cross-tabs syntax", phase: "Table Specs" },

  // Phase 5: Statistical Analysis (Steps 17-18)
  { step: 17, name: "Execute PSPP syntax", phase: "Analysis" },
  { step: 18, name: "Run statistical tests", phase: "Analysis" },

  // Phase 6: Filtering (Steps 19-20)
  { step: 19, name: "Filter significant tables", phase: "Filtering" },
  { step: 20, name: "Apply corrections", phase: "Filtering" },

  // Phase 7: Presentation (Steps 21-22)
  { step: 21, name: "Generate PowerPoint presentation", phase: "Presentation" },
  { step: 22, name: "Generate HTML dashboard", phase: "Presentation" },
];

interface WorkflowProgressProps {
  currentStep: number | null;
  className?: string;
  compact?: boolean;
}

/**
 * WorkflowProgress component displays the 22-step survey analysis workflow progress.
 *
 * @param currentStep - Current step number (0-22), null means not started
 * @param className - Additional CSS classes
 * @param compact - Whether to show compact version (just progress bar)
 */
export function WorkflowProgress({
  currentStep,
  className,
  compact = false,
}: WorkflowProgressProps) {
  // Determine which steps are completed, in progress, or pending
  const getStepStatus = (step: number) => {
    if (currentStep === null) return "pending";
    if (step < currentStep) return "completed";
    if (step === currentStep) return "in-progress";
    return "pending";
  };

  const progressPercentage = currentStep
    ? Math.round((currentStep / 22) * 100)
    : 0;

  const completedSteps = currentStep ? Math.max(0, currentStep - 1) : 0;

  if (compact) {
    return (
      <div className={cn("w-full", className)}>
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="font-medium text-gray-700">
            Analysis Progress
          </span>
          <span className="text-gray-500">
            Step {currentStep || 0} of 22 ({progressPercentage}%)
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className="bg-blue-600 h-2 transition-all duration-500 ease-out"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        {currentStep === 22 && (
          <p className="text-sm text-green-600 mt-2 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4" />
            Analysis Complete!
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={cn("w-full bg-white rounded-lg border p-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Survey Analysis Progress
          </h3>
          <p className="text-sm text-gray-600">
            {completedSteps} of {WORKFLOW_STEPS.length} steps completed
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {progressPercentage}%
          </div>
          {currentStep === 22 ? (
            <span className="text-sm text-green-600 font-medium flex items-center justify-end gap-1">
              <CheckCircle2 className="w-4 h-4" />
              Complete
            </span>
          ) : currentStep ? (
            <span className="text-sm text-blue-600">
              Step {currentStep} in progress
            </span>
          ) : (
            <span className="text-sm text-gray-500">Not started</span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-4 overflow-hidden">
        <div
          className="bg-blue-600 h-3 transition-all duration-500 ease-out relative overflow-hidden"
          style={{ width: `${progressPercentage}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
      </div>

      {/* Steps by Phase */}
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {Object.entries(
          WORKFLOW_STEPS.reduce((acc, step) => {
            if (!acc[step.phase]) {
              acc[step.phase] = [];
            }
            acc[step.phase].push(step);
            return acc;
          }, {} as Record<string, typeof WORKFLOW_STEPS>)
        ).map(([phase, steps]) => (
          <div key={phase} className="border-l-2 border-gray-200 pl-3">
            <div className="text-xs font-semibold text-gray-500 uppercase mb-1">
              {phase}
            </div>
            <div className="flex flex-wrap gap-1">
              {steps.map(({ step, name }) => {
                const status = getStepStatus(step);
                return (
                  <div
                    key={step}
                    className={cn(
                      "flex items-center gap-1 text-xs px-2 py-1 rounded-md",
                      status === "completed" &&
                        "bg-green-50 text-green-700 border border-green-200",
                      status === "in-progress" &&
                        "bg-blue-50 text-blue-700 border border-blue-200",
                      status === "pending" &&
                        "bg-gray-50 text-gray-500 border border-gray-200"
                    )}
                    title={name}
                  >
                    {status === "completed" && (
                      <CheckCircle2 className="w-3 h-3" />
                    )}
                    {status === "in-progress" && (
                      <LoaderCircle className="w-3 h-3 animate-spin" />
                    )}
                    {status === "pending" && <Circle className="w-3 h-3" />}
                    <span className="font-medium">{step}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Hook to extract current step from stream values
 */
export function useCurrentStep(streamValues: any): number | null {
  return streamValues?.current_step ?? null;
}
