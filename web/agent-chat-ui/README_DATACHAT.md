# Agent Chat UI - DataChat Configuration

This is a customized version of the [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) configured for the DataChat SPSS Analyzer application.

## Installation

Dependencies are already installed via pnpm. To reinstall:

```bash
pnpm install
```

## Configuration

### Environment Variables

The `.env.local` file contains the following configuration:

```bash
# LangGraph server URL (where the survey_analysis graph is hosted)
NEXT_PUBLIC_API_URL=http://localhost:8123

# Assistant/Graph ID (name of the LangGraph graph)
NEXT_PUBLIC_ASSISTANT_ID=survey_analysis

# Optional: LangSmith API Key for production deployments
LANGSMITH_API_KEY=
```

### Customizations

#### 1. SPSS .sav File Support

The UI has been customized to support uploading SPSS `.sav` files:

**Modified Files:**
- `src/hooks/use-file-upload.tsx` - Added .sav file types to supported formats
- `src/lib/multimodal-utils.ts` - Updated file conversion to handle .sav files

**Supported File Types:**
- Images: JPEG, PNG, GIF, WebP
- Documents: PDF
- SPSS Data Files: .sav (with MIME types: `application/x-spss-sav`, `application/x-spp`, `application/octet-stream`)

#### 2. 22-Step Workflow Progress Tracking

**New Components:**
- `src/components/thread/WorkflowProgress.tsx` - Full progress indicator showing all 22 steps
- `src/components/thread/StepIndicator.tsx` - Compact indicator showing current step

**Features:**
- Visual progress bar (0-100%)
- Step-by-step breakdown organized by phase
- Real-time updates as workflow progresses
- Color-coded status (completed, in-progress, pending)
- "Awaiting Review" badges for human-in-the-loop steps

#### 3. Output File Downloads

**New Components:**
- `src/components/thread/OutputFiles.tsx` - Display component for generated files
- `src/app/api/files/[...path]/route.ts` - API proxy for file downloads

**Features:**
- Automatic display of PowerPoint and HTML dashboard when analysis completes
- Download buttons for PowerPoint presentation (.pptx)
- Open in new tab for HTML dashboard
- Proper MIME type handling

#### 4. File Upload Size Limits

For large SPSS survey files, Next.js is configured to handle larger file uploads:

```javascript
// next.config.mjs
export default {
  experimental: {
    serverActions: {
      bodySizeLimit: "50mb",
    },
  },
}
```

## Development

### Start the Development Server

```bash
pnpm dev
```

The UI will be available at `http://localhost:3000`

### Start the LangGraph Server

In a separate terminal, from the project root:

```bash
# The LangGraph server should run on port 8123
# This is configured in agent/graph.py and started via langgraph-cli
langgraph dev --port 8123
```

## Usage

1. Open `http://localhost:3000` in your browser
2. The UI will automatically connect to the LangGraph server at `http://localhost:8123`
3. Upload your SPSS `.sav` file using the file upload button or drag-and-drop
4. Watch the progress indicator as the analysis runs through 22 steps
5. Review and approve at three checkpoints (recoding rules, indicators, table specifications)
6. Download the generated PowerPoint presentation and HTML dashboard

## Features

### User Interface
- **Branded Experience**: "DataChat" branding and survey-focused messaging
- **SPSS-First Upload**: File upload emphasizes .sav files over PDF/images
- **Progressive Disclosure**: Progress indicator expands/collapses based on workflow state

### Workflow Tracking
- **Compact Progress Bar**: Shows percentage complete with current step number
- **Full Progress View**: Expandable display showing all 22 steps organized by phase:
  - Phase 1: Data Extraction (Steps 1-3)
  - Phase 2: Recoding (Steps 4-8)
  - Phase 3: Indicators (Steps 9-11)
  - Phase 4: Table Specifications (Steps 12-16)
  - Phase 5: Statistical Analysis (Steps 17-18)
  - Phase 6: Filtering (Steps 19-20)
  - Phase 7: Presentation (Steps 21-22)

### Human-in-the-Loop
- **Step-Specific Indicators**: Visual badges for steps awaiting review (6, 11, 14)
- **Approve/Reject Interface**: Integration with existing agent-inbox components
- **Feedback Collection**: Text input for providing rejection feedback

### Output Delivery
- **Automatic Display**: Output files appear automatically when step 22 completes
- **File Type Icons**: Visual distinction between PowerPoint and HTML files
- **Direct Download**: One-click download or open in new tab

## Architecture

The Agent Chat UI connects to the LangGraph server via the `@langchain/langgraph-sdk`:

1. **Frontend**: Next.js 15 with React 19
2. **Styling**: Tailwind CSS with Radix UI components
3. **State Management**: LangGraph streaming with real-time updates
4. **File Handling**: Base64 encoding for file uploads
5. **API Proxy**: Next.js API routes proxy LangGraph backend requests

## Component Structure

```
src/components/thread/
├── index.tsx                 # Main thread component (modified for DataChat)
├── WorkflowProgress.tsx      # 22-step progress indicator (NEW)
├── StepIndicator.tsx         # Current step display (NEW)
├── OutputFiles.tsx           # Output file download component (NEW)
├── messages/
│   ├── ai.tsx               # AI message rendering
│   └── generic-interrupt.tsx # Generic interrupt display
└── agent-inbox/             # Human-in-the-loop review components
    └── components/
        ├── thread-actions-view.tsx
        └── inbox-item-input.tsx

src/app/api/
├── [..._path]/route.ts      # LangGraph API proxy (modified)
└── files/
    └── [...path]/route.ts    # File download proxy (NEW)
```

## Troubleshooting

### Connection Issues

If the UI cannot connect to the LangGraph server:
1. Verify the LangGraph server is running on port 8123
2. Check `.env.local` for correct `NEXT_PUBLIC_API_URL`
3. Check browser console for CORS errors

### File Upload Issues

If .sav files are rejected:
1. Verify the file has the `.sav` extension
2. Check browser console for MIME type errors
3. Ensure file size is within 50MB limit

### Download Issues

If output files don't appear:
1. Check that analysis completed step 22
2. Verify `stream.values` contains `powerpoint_file` and `html_dashboard_file`
3. Check browser console for API errors

### Build Errors

If you encounter build errors:
```bash
# Clear cache and reinstall
rm -rf .next node_modules
pnpm install
pnpm dev
```

## Production Deployment

For production deployment, refer to the main [README.md](./README.md) "Going to Production" section. Key changes:

1. Set `LANGGRAPH_API_URL` to your production LangGraph deployment
2. Set `LANGSMITH_API_KEY` for authentication
3. Update `NEXT_PUBLIC_API_URL` to your production domain + `/api`
4. Configure file serving for output files (may need static file hosting)
5. Consider implementing custom authentication for enhanced security

## Resources

- [Agent Chat UI Documentation](https://github.com/langchain-ai/agent-chat-ui)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [DataChat Project Documentation](../../docs/)
