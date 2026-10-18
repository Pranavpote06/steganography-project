import React, { useRef, useState } from 'react';
import { UploadCloud, File, X, CheckCircle2 } from 'lucide-react';

export default function FileDropzone({
  file,
  onFileSelect,
  onClear,
  accept,
  title = "Upload Media Carrier",
  subtitle = "Drag & drop file here, or click to browse",
  allowedExtensions = []
}) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={inputRef}
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
          }
        }}
        accept={accept}
        className="hidden"
      />

      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-cyan-400 bg-cyan-950/20 shadow-glow-cyan'
              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/70'
          }`}
        >
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
            <UploadCloud className="w-7 h-7 animate-pulse" />
          </div>
          <h4 className="text-base font-medium text-slate-100 mb-1">{title}</h4>
          <p className="text-xs text-slate-400 mb-3">{subtitle}</p>

          {allowedExtensions.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-1.5">
              {allowedExtensions.map((ext) => (
                <span
                  key={ext}
                  className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-cyan-300 border border-slate-700/60"
                >
                  {ext}
                </span>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-cyan-500/30 shadow-glow-cyan flex items-center justify-between">
          <div className="flex items-center gap-3.5 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/50 flex items-center justify-center text-cyan-400 shrink-0">
              <File className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-100 truncate">{file.name}</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Size: {formatSize(file.size)}
              </p>
            </div>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onClear();
              if (inputRef.current) inputRef.current.value = '';
            }}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
            title="Remove selected file"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
