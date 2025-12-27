'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2, Upload, X, File } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { postsApi, categoriesApi, filesApi, toAbsoluteUrl } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import type { Post, Category, FileResponse } from '@/types';

const postSchema = z.object({
  title: z.string().min(1, '제목을 입력해주세요').max(200, '제목은 200자 이내로 입력해주세요'),
  content: z.string().min(1, '내용을 입력해주세요'),
  category_id: z.number().optional().nullable(),
  is_published: z.boolean(),
});

type PostForm = z.infer<typeof postSchema>;

export default function EditPostPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const postId = Number(params.id);

  const [post, setPost] = useState<Post | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attachedFiles, setAttachedFiles] = useState<FileResponse[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<PostForm>({
    resolver: zodResolver(postSchema),
  });

  const categoryId = watch('category_id');

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await categoriesApi.getList();
        setCategories(data);
      } catch (err) {
        console.error('Failed to fetch categories:', err);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const postData = await postsApi.getById(postId);
        setPost(postData);
        setAttachedFiles(postData.files || []);
        reset({
          title: postData.title,
          content: postData.content,
          category_id: postData.category?.id || undefined,
          is_published: postData.is_published,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : '게시글을 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [postId, reset]);

  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setError(null);

    try {
      const uploadPromises = Array.from(files).map(file => filesApi.upload(file));
      const uploadedFiles = await Promise.all(uploadPromises);

      // 업로드된 파일의 상세 정보 가져오기
      const fileDetails = await Promise.all(
        uploadedFiles.map(f => filesApi.getById(f.id))
      );

      setAttachedFiles(prev => [...prev, ...fileDetails]);
    } catch (err) {
      setError(err instanceof Error ? err.message : '파일 업로드에 실패했습니다.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, []);

  const removeFile = useCallback((fileId: number) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  const onSubmit = async (data: PostForm) => {
    setError(null);
    try {
      await postsApi.update(postId, {
        ...data,
        category_id: data.category_id || undefined,
        file_ids: attachedFiles.map(f => f.id),
      });
      router.push(`/posts/${postId}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : '게시글 수정에 실패했습니다.';
      setError(message);
    }
  };

  // 권한 확인
  const canEdit = user && post && (user.id === post.author.id || user.role === 'admin');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="space-y-4">
        <Link href="/posts">
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            목록으로
          </Button>
        </Link>
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          {error || '게시글을 찾을 수 없습니다.'}
        </div>
      </div>
    );
  }

  if (!canEdit) {
    return (
      <div className="space-y-4">
        <Link href={`/posts/${postId}`}>
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </Link>
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          수정 권한이 없습니다.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href={`/posts/${postId}`}>
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">게시글 수정</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>게시글 수정</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-950 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">제목</Label>
              <Input
                id="title"
                placeholder="게시글 제목을 입력하세요"
                {...register('title')}
                disabled={isSubmitting}
              />
              {errors.title && (
                <p className="text-sm text-red-500">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">카테고리</Label>
              <Select
                value={categoryId?.toString() || 'none'}
                onValueChange={(value) => {
                  setValue('category_id', value === 'none' ? undefined : parseInt(value));
                }}
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue placeholder="카테고리 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">카테고리 없음</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id.toString()}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="content">내용</Label>
              <textarea
                id="content"
                placeholder="게시글 내용을 입력하세요"
                className="flex min-h-[300px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register('content')}
                disabled={isSubmitting}
              />
              {errors.content && (
                <p className="text-sm text-red-500">{errors.content.message}</p>
              )}
            </div>

            {/* 이미지 첨부 섹션 */}
            <div className="space-y-2">
              <Label>이미지 첨부</Label>
              <div className="border-2 border-dashed rounded-lg p-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                  id="file-upload"
                  disabled={isSubmitting || isUploading}
                />
                <label
                  htmlFor="file-upload"
                  className="flex flex-col items-center justify-center cursor-pointer py-4"
                >
                  {isUploading ? (
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  ) : (
                    <Upload className="h-8 w-8 text-muted-foreground" />
                  )}
                  <span className="mt-2 text-sm text-muted-foreground">
                    {isUploading ? '업로드 중...' : '클릭하여 이미지 선택'}
                  </span>
                </label>

                {/* 첨부된 파일 목록 */}
                {attachedFiles.length > 0 && (
                  <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                    {attachedFiles.map((file) => (
                      <div
                        key={file.id}
                        className="relative group rounded-lg overflow-hidden border bg-muted"
                      >
                        {file.is_image ? (
                          <img
                            src={toAbsoluteUrl(file.url)}
                            alt={file.alt_text || file.filename}
                            className="w-full h-24 object-cover"
                          />
                        ) : (
                          <div className="w-full h-24 flex items-center justify-center">
                            <File className="h-8 w-8 text-muted-foreground" />
                          </div>
                        )}
                        <button
                          type="button"
                          onClick={() => removeFile(file.id)}
                          className="absolute top-1 right-1 p-1 bg-black/50 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="h-4 w-4" />
                        </button>
                        <div className="p-1 text-xs truncate">{file.filename}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                이미지를 여러 개 선택할 수 있습니다. (최대 10MB)
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_published"
                {...register('is_published')}
                className="h-4 w-4 rounded border-gray-300"
                disabled={isSubmitting}
              />
              <Label htmlFor="is_published">공개</Label>
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isSubmitting || isUploading}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                수정하기
              </Button>
              <Link href={`/posts/${postId}`}>
                <Button type="button" variant="outline">
                  취소
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
