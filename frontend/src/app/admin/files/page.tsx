'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  MoreHorizontal,
  Trash2,
  Eye,
  Download,
  Image,
  File,
  FileText,
  Upload,
  Edit,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { FileUpload } from '@/components/ui/file-upload';
import { filesApi, toAbsoluteUrl } from '@/lib/api';
import type { FileResponse, StorageInfoResponse } from '@/types';
import { toast } from 'sonner';

export default function AdminFilesPage() {
  const [files, setFiles] = useState<FileResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileResponse | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [storageInfo, setStorageInfo] = useState<StorageInfoResponse | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Edit form
  const [editAltText, setEditAltText] = useState('');
  const [editDescription, setEditDescription] = useState('');

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const data = await filesApi.adminGetAll({
        page,
        size: 20,
        contentType: contentTypeFilter || undefined,
      });
      setFiles(data.items);
      setTotalPages(data.pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : '파일 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [page, contentTypeFilter]);

  const fetchStorageInfo = async () => {
    try {
      const info = await filesApi.getStorageInfo();
      setStorageInfo(info);
    } catch (err) {
      console.error('스토리지 정보 로드 실패:', err);
    }
  };

  useEffect(() => {
    fetchFiles();
    fetchStorageInfo();
  }, [fetchFiles]);

  const handleDelete = async () => {
    if (!selectedFile) return;
    setActionLoading(true);
    try {
      await filesApi.delete(selectedFile.id);
      toast.success('파일이 삭제되었습니다.');
      setDeleteDialogOpen(false);
      setSelectedFile(null);
      fetchFiles();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : '삭제에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpload = async (uploadFiles: File[]) => {
    try {
      if (uploadFiles.length === 1) {
        await filesApi.upload(uploadFiles[0]);
      } else {
        await filesApi.uploadMultiple(uploadFiles);
      }
      toast.success(`${uploadFiles.length}개 파일이 업로드되었습니다.`);
      setUploadDialogOpen(false);
      fetchFiles();
    } catch (err) {
      throw err;
    }
  };

  const handleEdit = async () => {
    if (!selectedFile) return;
    setActionLoading(true);
    try {
      await filesApi.update(selectedFile.id, {
        altText: editAltText,
        description: editDescription,
      });
      toast.success('파일 정보가 수정되었습니다.');
      setEditDialogOpen(false);
      setSelectedFile(null);
      fetchFiles();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : '수정에 실패했습니다.');
    } finally {
      setActionLoading(false);
    }
  };

  const openEditDialog = (file: FileResponse) => {
    setSelectedFile(file);
    setEditAltText(file.alt_text || '');
    setEditDescription(file.description || '');
    setEditDialogOpen(true);
  };

  const openDetailDialog = async (file: FileResponse) => {
    try {
      const detail = await filesApi.getById(file.id);
      setSelectedFile(detail);
      setDetailDialogOpen(true);
    } catch (err) {
      toast.error('파일 정보를 불러오는데 실패했습니다.');
    }
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) {
      return <Image className="h-4 w-4 text-blue-500" />;
    }
    if (contentType === 'application/pdf') {
      return <FileText className="h-4 w-4 text-red-500" />;
    }
    return <File className="h-4 w-4 text-gray-500" />;
  };

  const getStorageTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      local: 'bg-gray-500',
      supabase: 'bg-green-500',
      cloudflare: 'bg-orange-500',
      s3: 'bg-yellow-500',
    };
    return (
      <Badge className={colors[type] || 'bg-gray-500'}>
        {type.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">파일 관리</h1>
          <p className="text-muted-foreground">
            업로드된 모든 파일을 관리하세요
            {storageInfo && (
              <span className="ml-2">
                (스토리지: {storageInfo.storage_type.toUpperCase()})
              </span>
            )}
          </p>
        </div>
        <Button onClick={() => setUploadDialogOpen(true)}>
          <Upload className="mr-2 h-4 w-4" />
          파일 업로드
        </Button>
      </div>

      {/* 필터 */}
      <div className="flex gap-4">
        <Select
          value={contentTypeFilter}
          onValueChange={(value) => {
            setContentTypeFilter(value === 'all' ? '' : value);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="파일 타입" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체</SelectItem>
            <SelectItem value="image/">이미지</SelectItem>
            <SelectItem value="application/pdf">PDF</SelectItem>
            <SelectItem value="text/">텍스트</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 에러 */}
      {error && (
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          {error}
        </div>
      )}

      {/* 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle>파일 목록</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>파일</TableHead>
                  <TableHead>크기</TableHead>
                  <TableHead>스토리지</TableHead>
                  <TableHead>업로드 일시</TableHead>
                  <TableHead className="text-right">작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {files.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      파일이 없습니다.
                    </TableCell>
                  </TableRow>
                ) : (
                  files.map((file) => (
                    <TableRow key={file.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          {file.is_image ? (
                            <img
                              src={toAbsoluteUrl(file.url)}
                              alt={file.filename}
                              className="w-10 h-10 object-cover rounded"
                            />
                          ) : (
                            <div className="w-10 h-10 flex items-center justify-center bg-muted rounded">
                              {getFileIcon(file.content_type)}
                            </div>
                          )}
                          <div>
                            <p className="font-medium truncate max-w-xs">
                              {file.filename}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {file.content_type}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{file.size_formatted}</span>
                      </TableCell>
                      <TableCell>
                        {getStorageTypeBadge(file.storage_type)}
                      </TableCell>
                      <TableCell>
                        {new Date(file.created_at).toLocaleDateString('ko-KR', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" disabled={actionLoading}>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openDetailDialog(file)}>
                              <Eye className="mr-2 h-4 w-4" />
                              상세 보기
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => {
                                const a = document.createElement('a');
                                a.href = toAbsoluteUrl(file.url);
                                a.download = file.filename;
                                a.click();
                              }}
                            >
                              <Download className="mr-2 h-4 w-4" />
                              다운로드
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => openEditDialog(file)}>
                              <Edit className="mr-2 h-4 w-4" />
                              편집
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-500"
                              onClick={() => {
                                setSelectedFile(file);
                                setDeleteDialogOpen(true);
                              }}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              삭제
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}

          {/* 페이지네이션 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <Button
                variant="outline"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                이전
              </Button>
              <span className="text-sm text-muted-foreground">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                다음
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>파일 삭제</DialogTitle>
            <DialogDescription>
              정말로 &quot;{selectedFile?.filename}&quot; 파일을 삭제하시겠습니까?
              이 작업은 되돌릴 수 없습니다.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              취소
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={actionLoading}>
              {actionLoading ? '삭제 중...' : '삭제'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 업로드 다이얼로그 */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>파일 업로드</DialogTitle>
            <DialogDescription>
              {storageInfo && (
                <>
                  허용 확장자: {storageInfo.allowed_extensions.join(', ')}
                  <br />
                  최대 크기: {(storageInfo.max_file_size / (1024 * 1024)).toFixed(0)}MB
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <FileUpload
            onUpload={handleUpload}
            multiple
            maxSize={storageInfo?.max_file_size || 10 * 1024 * 1024}
            accept={storageInfo?.allowed_extensions.map((e) => `.${e}`).join(',') || '*'}
          />
        </DialogContent>
      </Dialog>

      {/* 편집 다이얼로그 */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>파일 정보 편집</DialogTitle>
            <DialogDescription>
              {selectedFile?.filename}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="alt_text">대체 텍스트</Label>
              <Input
                id="alt_text"
                value={editAltText}
                onChange={(e) => setEditAltText(e.target.value)}
                placeholder="이미지 설명 (접근성)"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">설명</Label>
              <Textarea
                id="description"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="파일에 대한 설명"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              취소
            </Button>
            <Button onClick={handleEdit} disabled={actionLoading}>
              {actionLoading ? '저장 중...' : '저장'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 상세 보기 다이얼로그 */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>파일 상세</DialogTitle>
          </DialogHeader>
          {selectedFile && (
            <div className="grid md:grid-cols-2 gap-6">
              {/* 미리보기 */}
              <div className="flex items-center justify-center bg-muted rounded-lg p-4">
                {selectedFile.is_image ? (
                  <img
                    src={toAbsoluteUrl(selectedFile.url)}
                    alt={selectedFile.alt_text || selectedFile.filename}
                    className="max-w-full max-h-64 object-contain rounded"
                  />
                ) : (
                  <div className="text-center">
                    <File className="h-16 w-16 text-muted-foreground mx-auto" />
                    <p className="mt-2 text-sm text-muted-foreground">
                      미리보기 불가
                    </p>
                  </div>
                )}
              </div>

              {/* 정보 */}
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">파일명</p>
                  <p className="font-medium break-all">{selectedFile.filename}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">크기</p>
                  <p>{selectedFile.size_formatted}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">타입</p>
                  <p>{selectedFile.content_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">스토리지</p>
                  <p>{getStorageTypeBadge(selectedFile.storage_type)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">업로드 일시</p>
                  <p>
                    {new Date(selectedFile.created_at).toLocaleString('ko-KR')}
                  </p>
                </div>
                {selectedFile.alt_text && (
                  <div>
                    <p className="text-sm text-muted-foreground">대체 텍스트</p>
                    <p>{selectedFile.alt_text}</p>
                  </div>
                )}
                {selectedFile.description && (
                  <div>
                    <p className="text-sm text-muted-foreground">설명</p>
                    <p>{selectedFile.description}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDetailDialogOpen(false);
                if (selectedFile) openEditDialog(selectedFile);
              }}
            >
              <Edit className="mr-2 h-4 w-4" />
              편집
            </Button>
            <Button onClick={() => window.open(toAbsoluteUrl(selectedFile?.url || ''), '_blank')}>
              <Download className="mr-2 h-4 w-4" />
              다운로드
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
