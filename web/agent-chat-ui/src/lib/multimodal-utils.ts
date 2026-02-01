import { ContentBlock } from "@langchain/core/messages";
import { toast } from "sonner";

// Returns a Promise of a typed multimodal block for images, PDFs, or SPSS files
export async function fileToContentBlock(
  file: File,
): Promise<ContentBlock.Multimodal.Data> {
  const supportedImageTypes = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
  ];
  const supportedFileTypes = [
    ...supportedImageTypes,
    "application/pdf",
    "application/x-spss-sav",
    "application/x-spp",
    "application/octet-stream", // Fallback for .sav files
  ];

  // Check if file type is supported or if it's a .sav file
  const isSavFile = file.name.endsWith('.sav') ||
                   file.type === "application/x-spss-sav" ||
                   file.type === "application/x-spp";

  if (!supportedFileTypes.includes(file.type) && !isSavFile) {
    toast.error(
      `Unsupported file type: ${file.type}. Supported types are: images, PDF, and SPSS .sav files`,
    );
    return Promise.reject(new Error(`Unsupported file type: ${file.type}`));
  }

  const data = await fileToBase64(file);

  if (supportedImageTypes.includes(file.type)) {
    return {
      type: "image",
      mimeType: file.type,
      data,
      metadata: { name: file.name },
    };
  }

  // PDF or SPSS .sav file
  if (isSavFile) {
    return {
      type: "file",
      mimeType: "application/x-spss-sav",
      data,
      metadata: { filename: file.name },
    };
  }

  // PDF
  return {
    type: "file",
    mimeType: "application/pdf",
    data,
    metadata: { filename: file.name },
  };
}

// Helper to convert File to base64 string
export async function fileToBase64(file: File): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      // Remove the data:...;base64, prefix
      resolve(result.split(",")[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Type guard for Base64ContentBlock
export function isBase64ContentBlock(
  block: unknown,
): block is ContentBlock.Multimodal.Data {
  if (typeof block !== "object" || block === null || !("type" in block))
    return false;
  // file type (legacy) - supports PDF and SPSS .sav files
  if (
    (block as { type: unknown }).type === "file" &&
    "mimeType" in block &&
    typeof (block as { mimeType?: unknown }).mimeType === "string" &&
    ((block as { mimeType: string }).mimeType.startsWith("image/") ||
      (block as { mimeType: string }).mimeType === "application/pdf" ||
      (block as { mimeType: string }).mimeType === "application/x-spss-sav" ||
      (block as { mimeType: string }).mimeType === "application/x-spp")
  ) {
    return true;
  }
  // image type (new)
  if (
    (block as { type: unknown }).type === "image" &&
    "mimeType" in block &&
    typeof (block as { mimeType?: unknown }).mimeType === "string" &&
    (block as { mimeType: string }).mimeType.startsWith("image/")
  ) {
    return true;
  }
  return false;
}
