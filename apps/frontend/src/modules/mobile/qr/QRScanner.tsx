import { useEffect, useRef } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

interface QRScannerProps {
  onScanSuccess: (decodedText: string) => void;
  onScanError?: (errorMessage: string) => void;
}

export default function QRScanner({ onScanSuccess, onScanError }: QRScannerProps) {
  const scannerElement = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!scannerElement.current) return;

    const config = {
      fps: 10,
      qrbox: { width: 280, height: 280 },
      rememberLastUsedCamera: true,
      supportedScanTypes: ["QR_CODE"],
    };

    const scanner = new Html5QrcodeScanner(scannerElement.current.id, config, false);

    scanner.render(
      (decodedText) => {
        onScanSuccess(decodedText);
      },
      (error) => {
        onScanError?.(error?.message ?? "QR scan error");
      },
    );

    return () => {
      scanner.clear().catch(() => undefined);
    };
  }, [onScanError, onScanSuccess]);

  return <div id="qr-reader" ref={scannerElement} style={{ width: "100%", minHeight: 360 }} />;
}
