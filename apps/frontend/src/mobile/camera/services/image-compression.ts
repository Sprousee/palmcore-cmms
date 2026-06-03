import imageCompression from "browser-image-compression";

export async function compressImageFile(file: File | Blob): Promise<Blob> {
  const inputFile = file instanceof File ? file : new File([file], "evidence.jpg", { type: file.type || "image/jpeg" });
  const options = {
    maxSizeMB: 1,
    maxWidthOrHeight: 1600,
    useWebWorker: true,
    initialQuality: 0.7,
    fileType: inputFile.type,
  };

  try {
    const compressedBlob = await imageCompression(inputFile, options);
    return compressedBlob;
  } catch (error) {
    return file;
  }
}
