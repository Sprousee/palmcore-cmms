import { useEffect, useRef, useState } from "react";
import { Html5Qrcode, Html5QrcodeCameraConfig, Html5QrcodeScannerState } from "html5-qrcode";

export interface UseQRScannerResult {
  scanning: boolean;
  error: string | null;
  flashAvailable: boolean;
  torchOn: boolean;
  cameraLabel: string;
  start: () => Promise<void>;
  stop: () => Promise<void>;
  toggleFlash: () => Promise<void>;
}

export function useQRScanner(onScanSuccess: (decodedText: string) => void): UseQRScannerResult {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flashAvailable, setFlashAvailable] = useState(false);
  const [torchOn, setTorchOn] = useState(false);
  const [cameraLabel, setCameraLabel] = useState("Cámara trasera");

  const html5QrcodeRef = useRef<Html5Qrcode | null>(null);
  const activeTrackRef = useRef<MediaStreamTrack | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    Html5Qrcode.getCameras()
      .then((cameras) => {
        const backCamera = cameras.find((camera) => camera.label.toLowerCase().includes("back") || camera.label.toLowerCase().includes("rear"));
        if (backCamera) {
          setCameraLabel(backCamera.label);
        }
      })
      .catch(() => {
        setCameraLabel("Cámara disponible");
      });

    return () => {
      void stop();
    };
  }, []);

  const playFeedback = () => {
    if (typeof navigator !== "undefined" && navigator.vibrate) {
      navigator.vibrate(50);
    }

    try {
      const audioContext = new AudioContext();
      const oscillator = audioContext.createOscillator();
      oscillator.frequency.value = 900;
      oscillator.connect(audioContext.destination);
      oscillator.start();
      setTimeout(() => {
        oscillator.stop();
        audioContext.close();
      }, 120);
    } catch {
      // Ignorar si no se puede reproducir audio.
    }
  };

  const stop = async () => {
    if (!html5QrcodeRef.current) return;
    try {
      await html5QrcodeRef.current.stop();
      await html5QrcodeRef.current.clear();
    } catch {
      // ignore cleanup failures
    } finally {
      setScanning(false);
      setTorchOn(false);
      activeTrackRef.current = null;
    }
  };

  const start = async () => {
    setError(null);
    if (scanning) return;

    if (typeof window === "undefined") {
      setError("El escáner solo está disponible en el navegador.");
      return;
    }

    const qrCodeRegionId = "qr-scanner";
    if (html5QrcodeRef.current === null) {
      html5QrcodeRef.current = new Html5Qrcode(qrCodeRegionId, { verbose: false });
    }

    const config = {
      fps: 10,
      qrbox: { width: 280, height: 280 },
      aspectRatio: 1.0,
      videoConstraints: { facingMode: { exact: "environment" } },
    };

    try {
      await html5QrcodeRef.current.start(
        { facingMode: { exact: "environment" } } as Html5QrcodeCameraConfig,
        config,
        (decodedText) => {
          playFeedback();
          onScanSuccess(decodedText);
        },
        () => {
          // No hay acción necesaria en cada lectura fallida.
        },
      );

      const track = (html5QrcodeRef.current as any).getRunningTrack?.();
      if (track) {
        activeTrackRef.current = track;
        const capabilities = track.getCapabilities?.();
        if (capabilities?.torch) {
          setFlashAvailable(true);
        }
      }

      setScanning(true);
    } catch (scanError) {
      setError("No se pudo iniciar el escáner. Verifica permisos de cámara.");
      setScanning(false);
    }
  };

  const toggleFlash = async () => {
    if (!activeTrackRef.current) return;
    try {
      const track = activeTrackRef.current;
      const capabilities = track.getCapabilities?.();
      if (!capabilities?.torch) {
        setError("La cámara no soporta flash.");
        return;
      }

      await track.applyConstraints({ advanced: [{ torch: !torchOn }] });
      setTorchOn(!torchOn);
    } catch {
      setError("No se pudo activar el flash.");
    }
  };

  return {
    scanning,
    error,
    flashAvailable,
    torchOn,
    cameraLabel,
    start,
    stop,
    toggleFlash,
  };
}
