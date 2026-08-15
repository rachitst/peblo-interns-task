import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Image as ImageIcon, Loader2 } from 'lucide-react';
import { Artwork, uploadArtwork } from '../api/client';

interface ArtworkDropzoneProps {
  episodeId: string;
  artworkType: 'poster' | 'banner' | 'thumbnail';
  existingArtwork?: Artwork;
  onUploadSuccess: (artwork: Artwork) => void;
}

const SPECS = {
  poster: {
    label: 'Poster Artwork',
    ratio: '2:3 Aspect Ratio',
    dimensions: '~600 × 900 px',
    maxSize: 'Max 200 KB',
    aspectClass: 'aspect-[2/3]',
  },
  banner: {
    label: 'Banner Artwork',
    ratio: '16:9 Aspect Ratio',
    dimensions: '~1280 × 720 px',
    maxSize: 'Max 200 KB',
    aspectClass: 'aspect-[16/9]',
  },
  thumbnail: {
    label: 'Thumbnail Artwork',
    ratio: '16:9 Aspect Ratio',
    dimensions: '~640 × 360 px',
    maxSize: 'Max 200 KB',
    aspectClass: 'aspect-[16/9]',
  },
};

export const ArtworkDropzone: React.FC<ArtworkDropzoneProps> = ({
  episodeId,
  artworkType,
  existingArtwork,
  onUploadSuccess,
}) => {
  const spec = SPECS[artworkType];
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(existingArtwork?.url || null);
  const [dimensions, setDimensions] = useState<{ width?: number; height?: number } | null>(
    existingArtwork?.width ? { width: existingArtwork.width, height: existingArtwork.height } : null
  );

  const handleFile = async (file: File) => {
    setErrorMessage(null);
    setIsUploading(true);

    try {
      const uploaded = await uploadArtwork(episodeId, artworkType, file);
      setPreviewUrl(uploaded.url || URL.createObjectURL(file));
      setDimensions({ width: uploaded.width, height: uploaded.height });
      onUploadSuccess(uploaded);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object' && detail.message) {
        setErrorMessage(detail.message);
      } else if (typeof detail === 'string') {
        setErrorMessage(detail);
      } else {
        setErrorMessage('Image failed validation. Please ensure valid dimensions and ≤200 KB.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex flex-col justify-between space-y-3">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-semibold text-sm text-slate-200">{spec.label}</h4>
          <p className="text-[11px] text-slate-400">{spec.ratio} · {spec.dimensions}</p>
        </div>
        <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
          {spec.maxSize}
        </span>
      </div>

      {/* Preview / Drop Container */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative ${spec.aspectClass} max-h-48 w-full rounded-xl border-2 border-dashed transition-all cursor-pointer flex flex-col items-center justify-center p-3 text-center overflow-hidden group ${
          previewUrl
            ? 'border-emerald-500/50 bg-slate-950'
            : 'border-slate-700 hover:border-indigo-500 bg-slate-950/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {previewUrl ? (
          <>
            <img
              src={previewUrl}
              alt={spec.label}
              className="absolute inset-0 w-full h-full object-cover group-hover:opacity-75 transition-opacity"
            />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white">
              <UploadCloud className="w-6 h-6 mb-1" />
              <span className="text-xs font-semibold">Click to Replace</span>
            </div>
            {dimensions?.width && (
              <span className="absolute bottom-2 left-2 bg-slate-950/80 backdrop-blur text-[10px] px-2 py-0.5 rounded font-mono text-emerald-300">
                {dimensions.width} × {dimensions.height} px
              </span>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center gap-1.5 text-slate-400 group-hover:text-indigo-400 transition-colors">
            {isUploading ? (
              <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            ) : (
              <UploadCloud className="w-6 h-6" />
            )}
            <span className="text-xs font-medium">Drag & drop or Click to upload</span>
            <span className="text-[10px] text-slate-500">JPG, PNG, WEBP</span>
          </div>
        )}
      </div>

      {/* Error Message Banner */}
      {errorMessage && (
        <div className="p-2.5 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <p className="leading-snug">{errorMessage}</p>
        </div>
      )}

      {/* Success Badge */}
      {previewUrl && !errorMessage && (
        <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-medium">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Uploaded & Validated</span>
        </div>
      )}
    </div>
  );
};
