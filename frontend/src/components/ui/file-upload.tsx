'use client';

import { useCallback, useState } from 'react';
import { Upload, X, File, Image, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // bytes
  maxFiles?: number;
  disabled?: boolean;
  className?: string;
}

interface PreviewFile {
  file: File;
  preview: string | null;
}

export function FileUpload({
  onUpload,
  accept = 'image/*,.pdf,.txt',
  multiple = false,
  maxSize = 10 * 1024 * 1024, // 10MB
  maxFiles = 10,
  disabled = false,
  className,
}: FileUploadProps) {
  const [files, setFiles] = useState<PreviewFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFiles = useCallback(
    (fileList: FileList | File[]): File[] => {
      const validFiles: File[] = [];
      const errors: string[] = [];

      const fileArray = Array.from(fileList);

      // 최대 파일 수 체크
      if (fileArray.length > maxFiles) {
        errors.push(`최대 ${maxFiles}개의 파일만 업로드할 수 있습니다.`);
        return [];
      }

      for (const file of fileArray) {
        // 파일 크기 체크
        if (file.size > maxSize) {
          errors.push(`${file.name}: 파일이 너무 큽니다. (최대 ${formatSize(maxSize)})`);
          continue;
        }

        validFiles.push(file);
      }

      if (errors.length > 0) {
        setError(errors.join('\n'));
      } else {
        setError(null);
      }

      return validFiles;
    },
    [maxSize, maxFiles]
  );

  const handleFiles = useCallback(
    (fileList: FileList | File[]) => {
      const validFiles = validateFiles(fileList);

      const newFiles: PreviewFile[] = validFiles.map((file) => ({
        file,
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
      }));

      if (multiple) {
        setFiles((prev) => [...prev, ...newFiles].slice(0, maxFiles));
      } else {
        // 단일 파일 모드에서는 기존 미리보기 URL 해제
        files.forEach((f) => f.preview && URL.revokeObjectURL(f.preview));
        setFiles(newFiles.slice(0, 1));
      }
    },
    [validateFiles, multiple, maxFiles, files]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      handleFiles(e.dataTransfer.files);
    },
    [handleFiles, disabled]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        handleFiles(e.target.files);
      }
    },
    [handleFiles]
  );

  const removeFile = useCallback((index: number) => {
    setFiles((prev) => {
      const file = prev[index];
      if (file.preview) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter((_, i) => i !== index);
    });
  }, []);

  const handleUpload = async () => {
    if (files.length === 0 || isUploading) return;

    setIsUploading(true);
    setError(null);

    try {
      await onUpload(files.map((f) => f.file));
      // 업로드 성공 후 파일 목록 초기화
      files.forEach((f) => f.preview && URL.revokeObjectURL(f.preview));
      setFiles([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : '업로드에 실패했습니다.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop Zone */}
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          isDragging ? 'border-primary bg-primary/5' : 'border-muted-foreground/25',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          disabled={disabled}
          className="hidden"
          id="file-upload-input"
        />
        <label
          htmlFor="file-upload-input"
          className={cn('cursor-pointer', disabled && 'cursor-not-allowed')}
        >
          <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-sm text-muted-foreground mb-2">
            파일을 드래그하거나 클릭하여 선택하세요
          </p>
          <p className="text-xs text-muted-foreground">
            최대 {formatSize(maxSize)} {multiple && `/ 최대 ${maxFiles}개`}
          </p>
        </label>
      </div>

      {/* Error */}
      {error && (
        <div className="text-sm text-red-500 whitespace-pre-line">{error}</div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 bg-muted rounded-lg"
            >
              {/* Preview */}
              {file.preview ? (
                <img
                  src={file.preview}
                  alt={file.file.name}
                  className="w-12 h-12 object-cover rounded"
                />
              ) : (
                <div className="w-12 h-12 flex items-center justify-center bg-background rounded">
                  <File className="h-6 w-6 text-muted-foreground" />
                </div>
              )}

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatSize(file.file.size)}
                </p>
              </div>

              {/* Remove Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFile(index)}
                disabled={isUploading}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}

          {/* Upload Button */}
          <Button
            onClick={handleUpload}
            disabled={isUploading || files.length === 0}
            className="w-full"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                업로드 중...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                {files.length}개 파일 업로드
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
