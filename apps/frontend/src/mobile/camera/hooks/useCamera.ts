import { useEffect, useRef, useState, type RefObject } from "react";

interface CaptureResult {
  file: Blob;
  fileName: string;
  mimeType: string;
  type: "photo" | "video";
}

interface UseCameraResult {
  videoRef: RefObject<HTMLVideoElement>;
  streamActive: boolean;
  cameraReady: boolean;
  recording: boolean;
  error: string | null;
  previewUrl: string | null;
  captureType: "photo" | "video" | null;
  startCamera: () => Promise<void>;
  stopCamera: () => Promise<void>;
  takePhoto: () => Promise<void>;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  resetPreview: () => void;
  captureResult: CaptureResult | null;
}

export function useCamera(): UseCameraResult {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);

  const [cameraReady, setCameraReady] = useState(false);
  const [streamActive, setStreamActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [captureType, setCaptureType] = useState<"photo" | "video" | null>(null);
  const [captureResult, setCaptureResult] = useState<CaptureResult | null>(null);

  useEffect(() => {
    return () => {
      void stopCamera();
    };
  }, []);

  const startCamera = async () => {
    setError(null);
    if (streamActive) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { exact: "environment" } },
        audio: true,
      });
      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStreamActive(true);
      setCameraReady(true);
    } catch (err) {
      setError("No se pudo acceder a la cámara. Verifica permisos y disponibilidad.");
      setStreamActive(false);
      setCameraReady(false);
    }
  };

  const stopCamera = async () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setStreamActive(false);
    setCameraReady(false);
    setRecording(false);
  };

  const takePhoto = async () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) {
      setError("No se pudo capturar la imagen.");
      return;
    }
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
    if (!blob) {
      setError("No se pudo generar el archivo de la foto.");
      return;
    }
    const fileName = `evidence-${Date.now()}.jpg`;
    const result = { file: blob, fileName, mimeType: blob.type, type: "photo" as const };
    setCaptureResult(result);
    setCaptureType("photo");
    setPreviewUrl(URL.createObjectURL(blob));
  };

  const startRecording = async () => {
    if (!mediaStreamRef.current) {
      setError("Inicia la cámara antes de grabar video.");
      return;
    }
    setError(null);
    recordedChunksRef.current = [];
    const recorder = new MediaRecorder(mediaStreamRef.current, { mimeType: "video/webm;codecs=vp8,opus" });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    recorder.onstop = async () => {
      const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
      const fileName = `evidence-${Date.now()}.webm`;
      const result = { file: blob, fileName, mimeType: blob.type, type: "video" as const };
      setCaptureResult(result);
      setCaptureType("video");
      setPreviewUrl(URL.createObjectURL(blob));
      setRecording(false);
    };

    recorder.start();
    setRecording(true);
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current || !recording) return;
    mediaRecorderRef.current.stop();
  };

  const resetPreview = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setCaptureType(null);
    setCaptureResult(null);
  };

  return {
    videoRef,
    streamActive,
    cameraReady,
    recording,
    error,
    previewUrl,
    captureType,
    startCamera,
    stopCamera,
    takePhoto,
    startRecording,
    stopRecording,
    resetPreview,
    captureResult,
  };
}
